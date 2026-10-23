import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = BASE_DIR / "server" / "todo_server.py"

llm = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
)
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def build_system_prompt() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")
    return f"""你是一个待办管理助手，可以调用工具帮用户管理待办事项。

当前时间：{now}。用户说“周五”“下周三”“明天”等相对时间时，先根据当前时间换算出具体日期，再作为 due 参数传入。

工作规则：
1. 用户要添加待办 → 调用 add_todo。若缺少标题先追问；截止时间模糊时自行推算具体日期。
2. 用户要查看待办 → 调用 list_todos，默认查 pending。返回结果要用中文列表总结，不要直接贴 JSON。
3. 用户要标记完成或删除 → 用户若没给 id，必须先调用 list_todos 查询并匹配标题，拿到 id 后再调 complete_todo/delete_todo，禁止凭空编造 id。
4. 用户问统计 → 调用 get_stats。
5. 回复简洁、用中文，可适度使用 emoji。不要暴露工具名和 JSON-RPC 细节。
"""


def mcp_tools_to_openai(tools) -> list[dict]:
    """把 MCP 工具列表转成 OpenAI tools 参数格式。"""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.input_schema,
            },
        }
        for t in tools
    ]


async def run_agent(session: ClientSession):
    # 1. 拉取工具清单
    tools_resp = await session.list_tools()
    openai_tools = mcp_tools_to_openai(tools_resp.tools)
    print(
        f"[已连接 MCP Server，可用工具：{', '.join(t.name for t in tools_resp.tools)}]\n"
    )

    messages = [{"role": "system", "content": build_system_prompt()}]

    # 2. 交互主循环
    while True:
        try:
            user_input = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # 3. Agent Loop：推理 → 调工具 → 再推理，直到模型不再要求调工具
        while True:
            resp = await llm.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=openai_tools,
                temperature=0.3,
            )
            msg = resp.choices[0].message

            if msg.tool_calls:
                # 回填 assistant 的 tool_calls 消息
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": [
                            {
                                "id": c.id,
                                "type": "function",
                                "function": {
                                    "name": c.function.name,
                                    "arguments": c.function.arguments,
                                },
                            }
                            for c in msg.tool_calls
                        ],
                    }
                )

                # 逐个执行工具
                for call in msg.tool_calls:
                    name = call.function.name
                    try:
                        args = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}

                    print(
                        f"  [调用工具] {name}({json.dumps(args, ensure_ascii=False)})"
                    )
                    try:
                        result = await session.call_tool(name, args)
                        text = (
                            "\n".join(
                                c.text
                                for c in result.content
                                if getattr(c, "type", "") == "text"
                            )
                            or "(工具无返回内容)"
                        )
                    except Exception as e:  # 工具执行异常也要回传给模型
                        text = f"工具执行出错：{e}"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": text,
                        }
                    )
                # 回到 while 顶部，带着工具结果继续让模型推理
                continue

            # 无 tool_calls → 最终回复
            print(f"\nAgent > {msg.content}\n")
            messages.append({"role": "assistant", "content": msg.content})
            break


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=[str(SERVER_SCRIPT)],
        env={**os.environ},
    )
    # Client 以子进程方式拉起 Server，通过 stdio 收发 JSON-RPC
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # MCP 握手
            await run_agent(session)


if __name__ == "__main__":
    asyncio.run(main())

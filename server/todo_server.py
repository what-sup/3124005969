import json
import os
from pathlib import Path
from datetime import datetime

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("todo-manager")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "todos.json"


# ---- 存储层（含路径/数据安全） ----
def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load() -> list[dict]:
    _ensure_dir()
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(todos: list[dict]) -> None:
    _ensure_dir()
    # 原子写：先写临时文件再替换，避免中途崩溃损坏数据
    tmp = DATA_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def _next_id(todos: list[dict]) -> int:
    return max((t["id"] for t in todos), default=0) + 1


# ---- 工具定义 ----
@mcp.tool()
def add_todo(
    title: str,
    due: str = "",
    category: str = "其他",
    priority: str = "medium",
) -> str:
    """添加一条待办事项。

    Args:
        title: 待办标题，必填，如“交软件工程作业”。
        due: 截止时间，ISO 格式字符串，如 "2026-05-22 15:00"；没有则留空。
        category: 分类，如“课程”“生活”“工作”，默认“其他”。
        priority: 优先级，可选 low/medium/high，默认 medium。
    """
    if not title or not title.strip():
        return "错误：待办标题不能为空。"

    todos = _load()
    todo = {
        "id": _next_id(todos),
        "title": title.strip(),
        "due": due.strip(),
        "category": category.strip() or "其他",
        "priority": priority if priority in ("low", "medium", "high") else "medium",
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    todos.append(todo)
    _save(todos)
    return f"已添加待办：{todo['title']}（id={todo['id']}，截止={todo['due'] or '无'}，优先级={todo['priority']}）"


@mcp.tool()
def list_todos(status: str = "all", category: str = "") -> str:
    """查询待办列表，返回 JSON 字符串。

    Args:
        status: 筛选状态，可选 pending（未完成）/done（已完成）/all（全部），默认 all。
        category: 按分类筛选，留空表示不筛选。
    """
    todos = _load()

    if status in ("pending", "done"):
        todos = [t for t in todos if t["status"] == status]
    if category:
        todos = [t for t in todos if t["category"] == category]

    if not todos:
        return "[]（当前没有符合条件的待办）"
    return json.dumps(todos, ensure_ascii=False, indent=2)


@mcp.tool()
def complete_todo(todo_id: int) -> str:
    """将指定 id 的待办标记为已完成。

    Args:
        todo_id: 待办编号（整数），可通过 list_todos 查询获得。
    """
    todos = _load()
    for t in todos:
        if t["id"] == todo_id:
            if t["status"] == "done":
                return f"待办 id={todo_id} 已经是完成状态。"
            t["status"] = "done"
            t["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save(todos)
            return f"已将“{t['title']}”（id={todo_id}）标记为完成。"
    return f"错误：未找到 id={todo_id} 的待办。"


@mcp.tool()
def delete_todo(todo_id: int) -> str:
    """删除指定 id 的待办事项。

    Args:
        todo_id: 待办编号（整数），可通过 list_todos 查询获得。
    """
    todos = _load()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            removed = todos.pop(i)
            _save(todos)
            return f"已删除待办：“{removed['title']}”（id={todo_id}）。"
    return f"错误：未找到 id={todo_id} 的待办。"


@mcp.tool()
def get_stats() -> str:
    """获取待办统计概览：总数、已完成、待办中、本周新增与完成数。"""
    todos = _load()
    total = len(todos)
    done = sum(1 for t in todos if t["status"] == "done")
    pending = total - done

    today = datetime.now()
    week_start = today.strftime("%Y-%m-%d")
    # 简化：按 created_at 日期前缀统计本周（生产环境应算真实周起止）
    this_week_created = sum(
        1 for t in todos if t.get("created_at", "")[:10] >= week_start
    )
    this_week_done = sum(
        1 for t in todos if t.get("completed_at", "")[:10] >= week_start
    )

    rate = f"{done / total * 100:.1f}%" if total else "0%"
    return (
        f"待办统计：总计 {total} 项，已完成 {done} 项（{rate}），"
        f"待办中 {pending} 项；本周新增 {this_week_created} 项，本周完成 {this_week_done} 项。"
    )


if __name__ == "__main__":
    # stdio 传输：由 Client 作为子进程拉起
    mcp.run(transport="stdio")

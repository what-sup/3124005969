# 🤖 智能待办管家 (Todo MCP Agent)

## 1. 项目名称与简介

**智能待办管家** 是一个基于 **Model Context Protocol (MCP)** 框架构建的“能说会做”的 AI 智能体。

传统的待办软件需要你手动点击“新建”、输入标题、选择日期。而这个智能体让你**只需用日常口语说出需求**，它就能听懂你的意图，并自动调用底层工具为你创建、查询、修改或删除待办事项。它不仅具备大模型优秀的自然语言交互能力（**会说**），还能真正操作本地文件修改你的数据（**会做**）。

## 2. 核心特性 (Features)

- 🗣️ **自然语言交互**：支持模糊时间理解。你说“下周三交作业”，它能自动推算出具体的日期。
- 🛠️ **MCP 工具调用**：基于官方 MCP 协议（stdio 传输），将 Python 函数安全地暴露给大模型执行。
- 🧠 **多步推理 (ReAct 模式)**：支持复杂指令。例如你说“删掉取快递”，它会先调用查询工具找到对应 ID，再调用删除工具。
- 💾 **数据持久化**：所有待办数据自动存入本地 `data/todos.json` 文件，关闭程序数据不丢失。
- 🔒 **安全与稳定**：限定了文件操作的安全路径，并采用“原子写入”机制防止数据损坏。

## 3. 快速开始 (Quick Start)

### 3.1 环境要求
- Python 3.10 及以上版本
- 一个大模型 API Key（本项目默认使用兼容 OpenAI SDK 的 **DeepSeek**）

### 3.2 安装依赖
克隆项目到本地后，在项目根目录打开终端：
```bash
# 建议在虚拟环境中运行
pip install -r requirements.txt
```

### 3.3 配置环境变量
1. 在根目录找到 `.env.example` 文件，复制一份并重命名为 `.env`。
2. 编辑 `.env` 文件，填入你真实的 API Key：
```env
LLM_API_KEY=sk-你的真实API_KEY
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```
*(注：`.env` 文件已被加入 `.gitignore`，不会被提交到远程仓库，保证密钥安全)*

### 3.4 启动项目
无需单独启动 Server，直接运行 Client 即可（Client 会作为父进程自动拉起 MCP Server 子进程）：
```bash
python client/agent.py
```
看到终端输出 `[已连接 MCP Server, 可用工具...]` 和 `你 >` 提示符，说明启动成功。

## 4. 使用示例 (Usage)

### 示例 1：智能添加待办
```text
你 > 帮我记一下，明天下午三点前交英语作业，挺急的

  [调用工具] add_todo({"title": "交英语作业", "due": "2024-05-24 15:00", "priority": "high"})

Agent > 好的，已为你添加：
        📌 交英语作业
        ⏰ 截止：明天 15:00
        🔴 优先级：高
```

### 示例 2：多步推理与状态变更
```text
你 > 英语作业写完了，帮我标记成完成

  [调用工具] list_todos({"status": "pending"})
  [调用工具] complete_todo({"todo_id": 1})

Agent > ✅ 已标记“交英语作业”为完成。剩余 0 项待办。
```

### 示例 3：统计概览
```text
你 > 最近完成情况怎么样？

  [调用工具] get_stats()

Agent > 📊 待办统计：
        总计：8 项
        已完成：5 项（62.5%）
        待办中：3 项
```

## 5. 技术架构 (Architecture)

### 5.1 运行流程图
本项目采用经典的 **MCP Client-Server 架构**，两者通过 stdio（标准输入输出）进行 JSON-RPC 通信：

```text
[用户输入] 
   │
   ▼
[Agent Client (agent.py)] ◄───► [LLM (DeepSeek / OpenAI SDK)]
   │
   │ (JSON-RPC over stdio)
   ▼
[MCP Server (todo_server.py)] ──► [本地数据 (data/todos.json)]
```

### 5.2 目录结构
```text
todo-mcp-agent/
├── README.md               # 项目说明文档
├── requirements.txt        # Python 依赖清单
├── .env.example            # 环境变量配置模板
├── client/
│   └── agent.py            # 客户端：负责大模型对话循环与 MCP 通信
├── server/
│   └── todo_server.py      # 服务端：定义待办管理的工具函数（会做）
└── data/
    └── todos.json          # 运行时自动生成的本地数据文件

# Agent Task Board

对话驱动的单文件任务看板。项目＝标签，3 行筛选，状态机，HTML 渲染。

## 解决的问题

Agent 对话本质上是**无状态的**——关掉终端上下文就没了。但任务有生命周期：创建、排队、执行、阻塞、完成。

- **跨会话持久化** — tasks.json 是 agent 的持久化大脑。新 session 读一次就知道全局状态，人不用重复上下文。
- **可观测性** — 五列看板 + 三行筛选 + 耗时显示，把 agent 内部状态外化成视觉接口。
- **人机节奏解耦** — 人当 PM（批量创建任务、设优先级、关联文档），agent 当执行者（按优先级自己拉任务做）。

## 安装

### Hermes Agent

```bash
git clone https://github.com/flowioo/agent-task-board.git
cd agent-task-board
bash install.sh
```

安装两个 skill：
- `task-board` — 创建/管理任务，渲染看板
- `task-loop` — 拉取 pending 任务执行，推进状态机

卸载：
```bash
rm ~/.hermes/skills/task-board ~/.hermes/skills/task-loop
```

### Claude Code

将 `skills/` 下的 SKILL.md 内容添加到项目的 `CLAUDE.md` 或 `.claude/commands/` 中：

```bash
# 方法一：添加到 CLAUDE.md
cat skills/task-board/SKILL.md >> CLAUDE.md
cat skills/task-loop/SKILL.md >> CLAUDE.md

# 方法二：作为命令添加
mkdir -p .claude/commands
cp skills/task-board/SKILL.md .claude/commands/task-board.md
cp skills/task-loop/SKILL.md .claude/commands/task-loop.md
```

### 其他 Agent（通用）

核心文件：
- `skills/task-board/SKILL.md` — 完整操作手册，包含状态机、渲染命令、路径约定
- `skills/task-board/scripts/render.py` — 看板渲染（Python3 + Jinja2）
- `skills/task-board/scripts/render-report.py` — 报告渲染
- `skills/task-board/templates/` — HTML 模板

将 SKILL.md 内容注入 agent 的 system prompt 或项目配置即可。

## 使用

```bash
# 打开看板
open ~/.project/board.html
```

在 agent 对话中：

| 你说 | Agent 动作 |
|------|-----------|
| 创建一个任务：实现用户登录 | 创建任务，status=pending |
| T-001 开始 | pending → in_progress |
| T-001 搞定了 | in_progress → done，生成报告 |
| T-001 阻塞了，因为 xxx | in_progress → blocked |
| T-001 不做了 | → cancelled |
| T-001 重新打开 | done/cancelled → pending |
| 看板 | open board.html |

## 状态机

```
pending → in_progress → done (终态)
   │           │
   │           ↓
   └──→ blocked → in_progress
   │
   └──→ cancelled (终态)
```

## 架构

```
~/.project/
  tasks.json                单文件，所有任务
  board.html                HTML 看板（自动生成）
  reports/T-NNN.html        完成报告（自动生成）
  docs/                     文档（软链）

skills/
  task-board/               看板管理 skill
    SKILL.md, templates/, scripts/, references/, docs/
  task-loop/                任务执行 skill
    SKILL.md
```

## 设计原则

- 深色主题 + emerald 单强调色（zinc 色板）
- Inter + JetBrains Mono 字体
- 项目=标签，不按目录隔离
- Jinja2 模板渲染，不拼 HTML 字符串
- 复制 ID 按钮 → 在 agent 中粘贴继续操作

## License

MIT

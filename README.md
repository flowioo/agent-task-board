# Task Board

对话驱动的单文件任务看板。项目＝标签，3 行筛选，状态机，HTML 渲染。

## 解决的问题

Agent 对话本质上是**无状态的**——关掉终端上下文就没了。但任务有生命周期：创建、排队、执行、阻塞、完成。

**跨会话持久化** — tasks.json 是 agent 的持久化大脑。新 session 读一次就知道全局状态，人不用重复上下文。

**可观测性** — 五列看板 + 三行筛选 + 耗时显示，把 agent 内部状态外化成视觉接口。哪个项目卡住了？哪个后端任务 pending？一眼看清。

**人机节奏解耦** — 人当 PM（批量创建任务、设优先级、关联文档），agent 当执行者（按优先级自己拉任务做）。blocked 时标记原因继续下一个，不等人。

## 架构

```
~/.project/
  tasks.json                单文件，所有任务
  board.html                HTML 看板（自动生成）
  reports/T-NNN.html        完成报告（自动生成）
  docs/ → 项目 docs/        文档软链

~/.hermes/skills/task-board/
  SKILL.md                  Hermes skill
  templates/board.html      Jinja2 看板模板
  templates/report.html     Jinja2 报告模板
  scripts/render.py         看板渲染
  scripts/render-report.py  报告渲染
  references/               设计决策记录
```

## 快速开始

```bash
# 打开看板
open ~/.project/board.html

# 创建任务（在 agent 对话中）
"创建一个任务：实现用户登录"

# 开始执行
"T-001 开始"

# 完成
"T-001 搞定了"
```

## 状态机

```
pending → in_progress → done (终态)
   │           │
   │           ↓
   └──→ blocked → in_progress
   │
   └──→ cancelled (终态)
```

## 三行筛选

项目(绿) AND 状态(橙) AND 标签(蓝)，行内 OR，行间 AND。

## 设计原则

- 深色主题 + emerald 单强调色
- Inter + JetBrains Mono 字体
- 标签不用于目录隔离，项目=标签
- 8px 半径统一，不做混合圆角系统
- 无 emoji 装饰链接

## License

MIT

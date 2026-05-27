---
name: task-board
description: 单文件任务看板。标签区分项目，HTML渲染，状态机，编号，文档关联，三行筛选，耗时显示。
version: 0.4.0
---

# Task Board Skill

单文件任务管理。对话驱动，自动渲染 HTML 看板。所有输出均为 HTML。

## 存储

```
~/.project/
  tasks.json              全部任务（单文件，项目=标签）
  board.html              看板（自动生成，勿手动编辑）
  reports/T-NNN.html      完成报告（自动生成）
```

## 项目 = 标签

创建任务时自动追加 cwd basename 到 tags。筛选栏第一行按项目标签过滤。
不要按目录隔离任务。所有项目共享 tasks.json。

## 操作速查

| 用户说 | 动作 | 状态转换 |
|--------|------|----------|
| 创建任务 xxx | 创建，status=pending | - |
| T-NNN 开始 | 锁定执行 | pending → in_progress |
| T-NNN 完成/搞定 | 标记完成 + 生成报告 | in_progress → done |
| T-NNN 阻塞了，因为 xxx | 标记阻塞 + 生成报告 | in_progress → blocked |
| T-NNN 取消/不做了 | 取消 | 非终态 → cancelled |
| T-NNN 重新打开 | 重开 | done/cancelled → pending |
| 给 T-NNN 关联 PRD xxx | 更新 docs.prd | - |
| 给 T-NNN 关联技术方案 xxx | 更新 docs.tech | - |
| 看板 | open board.html | - |
| 分析 xxx 项目/问题 | 分析后自动创建任务 | - |

## 分析 → 自动创建任务

当用户说"分析 xxx"或"这个项目推不动了"时，agent 应该：
1. 分析项目状态（文件、git log、现有任务）
2. 识别卡点和待办事项
3. **自动创建任务到看板**，不需要等用户说"创建任务"
4. 每个任务标注项目标签（cwd basename）+ 合适的 priority
5. 告知用户创建了哪些任务，推荐从哪个开始

这比用户手动一个个说"创建任务"更高效。

## 状态机

```
pending → in_progress → done
   │           │
   │           ↓
   └──→ blocked → in_progress
   │
   └──→ cancelled
```

done/cancelled 是终态。blocked 必须填 blocked_reason。done 必须填 completed_at。

## mention_at

每个任务有 `mention_at` 字段，表示"什么时候该关注这个任务"。
- 创建时 mention_at = created_at
- 状态变更时（开始/交接/阻塞解除）更新 mention_at = now
- 用于标记"这个任务该看了"的时刻

## 筛选记忆

看板用 localStorage 记住上次筛选状态（key: taskboard_filters）。
刷新页面自动恢复 project/status/tag 三行筛选。

## 渲染

每次 tasks.json 变更后必须重新渲染:
1. `python3 ~/.hermes/skills/task-board/scripts/render.py` — 生成 ~/.project/board.html
2. 如果 done/blocked: `python3 ~/.hermes/skills/task-board/scripts/render-report.py ~/.project/tasks.json T-NNN` — 生成报告

脚本路径是绝对路径（~/.hermes/skills/task-board/scripts/）。
render.py 默认读写 ~/.project/ 下的 tasks.json 和 board.html。

三行筛选: 项目(绿) AND 状态(橙) AND 标签(蓝)
耗时: done=completed_at-created_at, 其他=now-created_at

## 路径陷阱

board.html 位于 ~/.project/board.html。卡片中的链接（report、docs）是相对于此位置的。
- 报告路径应存为 `reports/T-NNN.html`（不含前缀）
- 文档路径应存为 `docs/xxx.md`（不含前缀，相对于 ~/.project/）
- 不要在路径前加 `.tasks/` 或其他前缀，那是旧架构的残留

## 复制 ID 按钮

每张卡片上有复制按钮（hover 显示），点击复制任务 ID（如 T-001）到剪贴板。
用途：复制后在 agent 对话中粘贴 ID，针对该任务继续操作。
实现：模板中 copyId() 函数 + clipboard API + 底部 toast 提示。

## 输出格式

所有文档输出均为 HTML。不要生成 .md 报告。
看板和报告使用深色主题：zinc 色板 + emerald 单一强调色 + Inter/JetBrains Mono 字体。
不要使用 emoji 装饰链接文字（不要用 📄📊 等 emoji 作为链接文本）。

## 文件引用

- `templates/board.html` — 看板模板
- `templates/report.html` — 报告模板
- `scripts/render.py` — 看板渲染
- `scripts/render-report.py` — 报告渲染
- `references/taste-skill-design-notes.md` — 看板视觉设计原则（来自 taste-skill）
- `references/design-decisions.md` — 架构决策记录

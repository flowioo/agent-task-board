---
name: task-loop
description: 从任务看板拉取 pending 任务，执行并推进状态机。适合手动触发或 cron 驱动。
version: 0.2.1
---

# Task Loop Skill

从 `~/.project/tasks.json` 拉取 pending 任务执行。

## 每个 Tick 流程

### 1. 拉取

从 ~/.project/tasks.json 筛选 pending 任务，按 priority(P1>P2>P3) + id 升序取第一个。

无 pending → 回复"没有待办任务"，结束。

### 2. 锁定 pending → in_progress

校验当前状态必须是 pending。更新 status + updated_at，写回 + 渲染 board.html。

### 3. 执行

根据 title 关键词判断类型:
- 含"实现/开发/修复/build" → delegate_task 委托 coding agent
- 含"调研/研究/research" → 搜索 + 总结
- 含"文档/doc/PRD" → 直接输出
- 其他 → 理解意图后执行

如果 docs.tech 有值 → 读取作为上下文。
如果 docs.prd 有值 → 读取理解目标。

### 4. 推进状态

成功 → done:
- 填 completed_at，追加 notes
- 写回 + 渲染 board.html + 渲染 HTML 报告
- 报告命令: `python3 ~/.hermes/skills/task-board/scripts/render-report.py ~/.project/tasks.json T-NNN`
- 回复: `✅ T-NNN 完成: {title}`

阻塞 → blocked:
- 填 blocked_reason，追加 notes
- 写回 + 渲染 board.html + 渲染 HTML 报告
- 回复: `🚧 T-NNN 被阻塞: {blocked_reason}`

失败（非用户取消）→ blocked（不是 cancelled）

### 5. 循环判断

还有 pending → 询问是否继续。Cron 模式下每个 tick 只做一个。

## 约束

- 每个 tick 只做一个任务
- done/cancelled 终态不可变
- 状态转换前必须校验合法性
- 编码任务委托 coding agent，不自己写
- 单任务上限 10 分钟，超时自动 blocked

## 渲染

- 看板: `python3 ~/.hermes/skills/task-board/scripts/render.py`
- 报告: `python3 ~/.hermes/skills/task-board/scripts/render-report.py ~/.project/tasks.json T-NNN`
- 每次 done/blocked 必须同时渲染看板 + 报告
- 报告生成后更新 tasks.json 中对应任务的 report 字段为 `reports/T-NNN.html`

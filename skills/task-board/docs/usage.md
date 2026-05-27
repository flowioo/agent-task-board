Task Board 使用手册
版本: 0.3.0
更新: 2026-05-26

═══════════════════════════════════════
1. 快速开始
═══════════════════════════════════════

打开看板:
  open ~/.project/board.html

创建第一个任务:
  你: 创建一个任务：实现用户登录
  Agent: 已创建 T-001: 实现用户登录 [pending] #backend #cc

看任务列表:
  你: 看板
  Agent: 打开 ~/.project/board.html

═══════════════════════════════════════
2. 任务操作
═══════════════════════════════════════

创建任务:
  你: 创建一个任务：实现用户登录
  你: 加个任务：优化首页加载速度，P1
  你: new task: 写单元测试
  效果: 自动分配 T-NNN 编号，状态设为 pending
  自动追加当前目录名（如 cc）作为项目标签

开始任务:
  你: T-001 开始
  你: 做登录那个任务
  你: start T-003
  效果: pending → in_progress

完成任务:
  你: T-001 搞定了
  你: 登录任务完成
  你: done T-001
  效果: in_progress → done，自动填 completed_at，生成 HTML 报告

阻塞任务:
  你: T-004 阻塞了，等商务提供商户号
  你: 支付网关卡住了，需要商户资质
  效果: in_progress → blocked，必须说明原因
  卡片上显示红色阻塞原因

取消任务:
  你: T-005 不做了
  你: 取消数据库迁移那个任务
  效果: 任何非终态 → cancelled

重新打开:
  你: T-002 重新打开
  你: reopen T-001
  效果: done/cancelled → pending

═══════════════════════════════════════
3. 标签和项目
═══════════════════════════════════════

自动识别:
  在 ~/Documents/lab/cc 目录下创建任务 → 自动加 cc 标签
  在 ~/Projects/montessori-app/ 下创建 → 自动加 montessori-app 标签

手动指定:
  你: 创建任务 xxx，项目 montessori-app
  你: 给 T-001 加标签 auth

多标签:
  你: 创建任务 xxx，标签 backend auth
  标签在卡片上显示为小标签，项目标签用绿色背景

看板筛选:
  第一行"项目": 点 cc 只看 cc 项目的任务
  第三行"标签": 点 backend 只看含 backend 标签的任务
  多个标签是 OR 关系（满足任一即显示）

═══════════════════════════════════════
4. 文档关联
═══════════════════════════════════════

关联 PRD:
  你: 给 T-001 关联 PRD docs/prd-v1-login.md

关联技术方案:
  你: T-001 关联技术方案 docs/tech-v1-login.md

效果: 卡片上出现 📄 PRD 和 📐 Tech Spec 链接，点击可查看

═══════════════════════════════════════
5. 看板使用
═══════════════════════════════════════

打开方式:
  open ~/.project/board.html

五列看板:
  ⏳ Pending       等待开始的任务
  🔧 In Progress   正在进行的任务
  🚧 Blocked       被阻塞的任务
  ✅ Done          已完成的任务
  ❌ Cancelled     已取消的任务

三行筛选:
  项目行（绿色）: 筛选项目，如 cc、montessori-app
  状态行（橙色）: 筛选状态
  标签行（蓝色）: 筛选标签，如 backend、frontend、test

  操作: 点击按钮激活/取消，三行之间 AND 关系
  示例: 选"cc" + 选"in_progress" → 只看 cc 项目中正在进行的任务

卡片信息:
  左上: 任务编号（T-001）
  右上: 耗时（⏱ 2h 15m / ⏳ 30m / 🚧 1h）
  标题: 任务标题
  标签: P2 + 项目标签(绿色) + 普通标签
  链接: 📄 PRD / 📐 Tech Spec / 📊 Report
  底部: 创建时间 + 更新时间

耗时含义:
  ⏱  — 已耗时（done 任务显示总耗时，in_progress 显示进行中耗时）
  ⏳  — 等待中（pending 任务从创建到现在）
  🚧  — 阻塞中（blocked 任务，红色高亮）

优先级颜色:
  左边框红色 = P1（最高优先级）
  左边框橙色 = P2
  左边框灰色 = P3

═══════════════════════════════════════
6. 报告
═══════════════════════════════════════

任务完成或阻塞后自动生成报告。

查看报告:
  方式一: 看板卡片上点 📊 Report 链接
  方式二: open ~/.project/reports/T-001.html

报告内容:
  - 任务标题和 ID
  - 结果标签（PASS / BLOCKED）
  - 检查项表格（来自 notes 中的 ✅/❌ 项）
  - 状态流时间线
  - 备注
  - 返回看板链接

═══════════════════════════════════════
7. 常见场景
═══════════════════════════════════════

场景一: 从创建到完成

  你: 创建任务：实现用户登录功能
  Agent: 已创建 T-008: 实现用户登录功能 [pending] #backend #cc

  你: T-008 开始
  Agent: [cc] T-008 [pending → in_progress]

  （agent 执行任务...）

  你: T-008 搞定了
  Agent: ✅ T-008 完成: 实现用户登录功能

场景二: 任务被阻塞

  你: 创建任务：对接微信支付
  Agent: 已创建 T-009: 对接微信支付 [pending] #payment #cc

  你: T-009 开始
  Agent: [cc] T-009 [pending → in_progress]

  你: T-009 阻塞了，等待商务提供商户号和密钥
  Agent: 🚧 T-009 被阻塞: 等待商务提供商户号和密钥

  （商户号到了...）

  你: T-009 继续，密钥拿到了
  Agent: [cc] T-009 [blocked → in_progress]

场景三: 取消再重开

  你: T-005 不做了，改用 ORM 自动迁移
  Agent: [cc] T-005 [pending → cancelled]

  你: 等等，还是需要手动迁移，T-005 重新打开
  Agent: [cc] T-005 [cancelled → pending]

场景四: 关联文档

  你: 创建任务：优化首页性能，标签 frontend performance
  Agent: 已创建 T-010: 优化首页性能 [pending] #frontend #performance #cc

  你: 给 T-010 关联 PRD docs/prd-perf.md 和技术方案 docs/tech-perf.md
  Agent: T-010 已关联 PRD 和技术方案

场景五: 按项目筛选

  你: 看板
  Agent: 打开 ~/.project/board.html

  （在看板中点击项目行的 montessori-app 按钮）
  → 只显示 montessori-app 项目的任务

场景六: 跨项目任务管理

  你: 创建任务：修复 hermes 的 Ctrl+J 问题，项目 hermes-agent
  Agent: 已创建 T-011: 修复 hermes 的 Ctrl+J 问题 [pending] #hermes-agent

  你: 看板
  （看板项目行出现 cc 和 hermes-agent 两个按钮）

场景七: 组合筛选

  你: 看板
  （在看板中: 选项目 cc + 选状态 blocked + 选标签 backend）
  → 只看 cc 项目中被阻塞的后端任务

═══════════════════════════════════════
8. 自动执行（task-loop）
═══════════════════════════════════════

手动触发:
  你: task-loop 开始执行
  Agent 拉取最高优先级的 pending 任务，执行并推进状态。

执行规则:
  - 每个 tick 只做一个任务
  - 优先级排序: P1 > P2 > P3，同优先级按 ID 升序
  - 成功 → done（生成报告）
  - 阻塞 → blocked（填原因 + 生成报告）
  - 编码任务委托给 coding agent

Cron 模式:
  可配置 cron job 每 2 小时自动拉取任务执行。
  无人值守模式，每个 tick 一个任务。

═══════════════════════════════════════
9. 数据位置
═══════════════════════════════════════

任务数据:   ~/.project/tasks.json
看板:       ~/.project/board.html
报告:       ~/.project/reports/T-NNN.html

备份:
  cp ~/.project/tasks.json ~/.project/tasks.json.bak

数据全是 JSON + HTML，可以直接 git 管理。

Task Board 设计文档
版本: 0.3.0
更新: 2026-05-26

═══════════════════════════════════════
1. 架构概述
═══════════════════════════════════════

核心理念: 单文件存储、标签区分项目、静态 HTML 渲染。

单文件 JSON:
  所有任务数据存储在 ~/.project/tasks.json。
  不依赖数据库，不拆分文件，方便备份和版本控制。

标签区分项目:
  项目概念被降级为普通标签。创建任务时自动追加 cwd basename
  作为项目标签。没有独立的项目实体，项目维度通过筛选体现。

HTML 渲染:
  看板是静态 HTML (~/.project/board.html)，由 Python 脚本渲染。
  每次任务变更后重新生成。浏览器直接打开即可查看。
  任务报告生成独立 HTML 文件 reports/T-NNN.html。

对话驱动:
  用户通过自然语言对话管理任务，agent 负责读写 JSON 和渲染 HTML。
  不需要命令行工具或 Web 服务。

═══════════════════════════════════════
2. 文件结构
═══════════════════════════════════════

~/.project/
  tasks.json              全部任务数据（单文件）
  board.html              看板页面（自动生成，不要手动编辑）
  reports/
    T-001.html            任务完成报告
    T-002.html
    ...

Hermes Skill 文件:

~/.hermes/skills/task-board/
  SKILL.md                设计文档（你正在读的）
  templates/
    board.html            看板 HTML 模板
    report.html           报告 HTML 模板
  scripts/
    render.py             看板渲染脚本
    render-report.py      报告渲染脚本

~/.hermes/skills/task-loop/
  SKILL.md                任务循环执行文档

═══════════════════════════════════════
3. 数据模型
═══════════════════════════════════════

tasks.json 顶层结构:

{
  "next_id": 8,
  "tasks": [ ... ]
}

任务对象字段:

id            string   自动   任务编号，格式 T-NNN，全局自增，不可复用
title         string   必填   一句话描述任务
description   string   可选   详细说明
status        string   自动   状态机当前状态，见第4节
priority      string   可选   P1/P2/P3，默认 P2
tags          string[] 可选   标签数组，项目名也放在这里
docs.prd      string   可选   PRD 文档路径
docs.tech     string   可选   技术方案文档路径
assignee      string   可选   agent 或 user
blocked_reason string  条件   仅 blocked 状态时必填
created_at    string   自动   ISO 8601 创建时间，只填一次不可改
updated_at    string   自动   ISO 8601 每次变更时更新
completed_at  string   条件   仅 done 状态时填，ISO 8601
notes         string[] 可选   备注、决策记录、检查项
report        string   可选   报告路径 reports/T-NNN.html

示例:

{
  "id": "T-001",
  "title": "验证 task-board skill",
  "description": "测试完整流程：创建、状态变更、HTML渲染",
  "status": "done",
  "priority": "P2",
  "tags": ["test", "cc"],
  "docs": {},
  "assignee": "agent",
  "blocked_reason": null,
  "created_at": "2026-05-26T21:23:59",
  "updated_at": "2026-05-26T21:54:41",
  "completed_at": "2026-05-26T21:54:41",
  "notes": ["8/8 checks passed"],
  "report": "reports/T-001.html"
}

═══════════════════════════════════════
4. 状态机
═══════════════════════════════════════

5 个状态:

  pending       已创建，等待开始
  in_progress   正在进行
  blocked       遇到阻塞，需要外部输入
  done          已完成（终态）
  cancelled     已取消（终态）

转换图:

  pending ──→ in_progress ──→ done
    │              │
    │              ↓
    └─────→  blocked ──→ in_progress
    │
    └──────────→ cancelled

合法转换表:

  当前状态        可转换到
  ──────────────────────────────────
  pending         in_progress, cancelled
  in_progress     done, blocked, cancelled
  blocked         in_progress, cancelled
  done            （终态，不可变）
  cancelled       （终态，不可变）

状态转换命令:

  用户说                →  动作
  ──────────────────────────────────────────
  创建任务 / 加个任务   →  创建，status = pending
  开始 / 做 / start     →  pending/blocked → in_progress
  完成 / 搞定 / done    →  in_progress → done
  阻塞 / 卡住了         →  in_progress → blocked（必填 blocked_reason）
  取消 / 不做了         →  任何非终态 → cancelled
  重新打开 / reopen     →  done/cancelled → pending

约束:
  - blocked 必须填 blocked_reason
  - done 必须填 completed_at
  - 每次 status 变更必须更新 updated_at
  - done 和 cancelled 是终态，不允许再改

═══════════════════════════════════════
5. 筛选设计
═══════════════════════════════════════

看板提供三行筛选器:

第一行 — 项目（绿色标识）
  列出所有被识别为"项目"的标签。
  项目标签的识别规则:
    a) 标签名匹配 ~/Documents/lab/ 等目录下的子目录名
    b) 标签出现在全部任务上（覆盖率 100%）
  支持多选，行内 OR 逻辑。

第二行 — 状态（橙色标识）
  列出 5 个状态: pending / in_progress / blocked / done / cancelled。
  每个按钮显示该状态的任务数量。
  支持多选，行内 OR 逻辑。

第三行 — 标签（蓝色标识）
  列出所有非项目标签。
  支持多选，行内 OR 逻辑。

行间关系: AND
  三行筛选器之间是 AND 逻辑，任务必须同时满足三行条件才显示。
  任意一行未选择任何项时，该行不参与筛选（等同于"全部"）。

列头计数联动:
  筛选后，每列的头部计数实时更新，显示 visible/total 格式。

═══════════════════════════════════════
6. 耗时显示
═══════════════════════════════════════

每张卡片右上角显示耗时，根据状态计算:

  状态           计算方式                      前缀
  ────────────────────────────────────────────────
  done           completed_at - created_at     ⏱
  in_progress    now - created_at              ⏱
  pending        now - created_at              ⏳
  blocked        now - created_at              🚧（红色）
  cancelled      now - created_at              无

显示格式:
  < 60秒       →  "30s"
  < 1小时      →  "25m"
  >= 1小时     →  "2h 15m" 或 "1h"

注意: pending/in_progress/blocked/cancelled 的耗时是渲染时刻计算的，
页面刷新后才会更新（静态 HTML）。

═══════════════════════════════════════
7. 项目自动匹配
═══════════════════════════════════════

创建任务时，按以下优先级确定项目标签:

  优先级   来源                     示例
  ────────────────────────────────────────────────────
  1        用户显式指定             "在 montessori-app 项目创建任务"
  2        cwd basename             /Users/baiju/Documents/lab/cc → cc
  3        git remote URL 最后一段  github.com/foo/my-app.git → my-app

匹配到的项目名自动追加到 tags 数组。

项目标签在筛选栏的"项目"行中显示，卡片上用绿色背景区分。

═══════════════════════════════════════
8. 文档关联
═══════════════════════════════════════

任务可以关联 PRD 和技术方案文档:

  docs.prd    PRD / 需求文档路径
  docs.tech   技术方案文档路径

关联方式:
  用户说"给 T-001 关联 PRD docs/prd-v1.md"
  agent 更新 docs.prd 字段。

卡片上显示为可点击链接（📄 PRD / 📐 Tech Spec）。

═══════════════════════════════════════
9. 报告
═══════════════════════════════════════

任务完成(done)或被阻塞(blocked)时，自动生成 HTML 报告。

报告路径: ~/.project/reports/T-NNN.html

报告内容:
  - 任务 ID + 标题
  - 结果标签（PASS / BLOCKED）
  - 检查项表格（从 notes 中提取含 ✅/❌ 的行）
  - 状态流（pending → in_progress → done）
  - 备注列表
  - 返回看板链接（← Back to Board）

看板卡片上显示 📊 Report 链接。

#!/usr/bin/env python3
"""Render tasks.json → board.html. 3-row filters: project / status / tags. Elapsed time."""

import json
import sys
import os
from datetime import datetime
from collections import Counter

STATUSES = ["pending", "in_progress", "blocked", "done", "cancelled"]
STATUS_LABELS = {
    "pending": "⏳ Pending",
    "in_progress": "🔧 In Progress",
    "blocked": "🚧 Blocked",
    "done": "✅ Done",
    "cancelled": "❌ Cancelled",
}

def fmt_elapsed(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds / 60)}m"
    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    if m == 0:
        return f"{h}h"
    return f"{h}h {m}m"

def calc_elapsed(task):
    created = task.get("created_at", "")
    if not created:
        return None, ""
    try:
        created_dt = datetime.fromisoformat(created)
    except ValueError:
        return None, ""

    status = task.get("status", "pending")

    if status == "done" and task.get("completed_at"):
        try:
            end_dt = datetime.fromisoformat(task["completed_at"])
            secs = (end_dt - created_dt).total_seconds()
            if secs < 0: secs = 0
            return secs, f"⏱ {fmt_elapsed(secs)}"
        except ValueError:
            pass

    now = datetime.now()
    secs = (now - created_dt).total_seconds()
    if secs < 0: secs = 0

    if status == "blocked":
        return secs, f"🚧 {fmt_elapsed(secs)}"
    elif status == "pending":
        return secs, f"⏳ {fmt_elapsed(secs)}"
    elif status == "in_progress":
        return secs, f"⏱ {fmt_elapsed(secs)}"
    else:
        return secs, fmt_elapsed(secs)


def render_card(task, project_tags):
    tid = task["id"]
    title = task["title"]
    desc = task.get("description", "")
    priority = task.get("priority", "P2")
    tags = task.get("tags", [])
    docs = task.get("docs", {})
    blocked = task.get("blocked_reason")
    assignee = task.get("assignee", "")
    created = task.get("created_at", "")[:10]
    updated = task.get("updated_at", "")[:10]
    notes = task.get("notes", [])
    status = task.get("status", "pending")

    _, elapsed_str = calc_elapsed(task)
    elapsed_class = "elapsed-blocked" if status == "blocked" else ""

    # separate project tags vs normal tags
    proj_on_card = [t for t in tags if t in project_tags]
    normal_tags = [t for t in tags if t not in project_tags]

    parts = [f'<div class="card" data-priority="{priority}" data-tags="{",".join(normal_tags)}" data-projects="{",".join(proj_on_card)}" data-status="{status}">']
    parts.append(f'<div class="card-top">')
    parts.append(f'<div class="card-id-wrap"><span class="card-id">{tid}</span><button class="copy-btn" onclick="copyId(\'{tid}\')" title="Copy {tid}"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="10" height="10" rx="1.5"/><path d="M4 5V3.5A1.5 1.5 0 0 1 5.5 2H12a2 2 0 0 1 2 2v6.5a1.5 1.5 0 0 1-1.5 1.5H11"/></svg></button></div>')
    if elapsed_str:
        parts.append(f'<span class="card-elapsed {elapsed_class}">{elapsed_str}</span>')
    parts.append(f'</div>')
    parts.append(f'<div class="card-title">{title}</div>')
    if desc:
        parts.append(f'<div class="card-desc">{desc}</div>')

    # tags: priority + project + normal
    tag_html = f'<span class="tag tag-priority tag-p{priority[1]}">{priority}</span>'
    for t in proj_on_card:
        tag_html += f' <span class="tag tag-project">{t}</span>'
    for t in normal_tags:
        tag_html += f' <span class="tag">{t}</span>'
    parts.append(f'<div>{tag_html}</div>')

    # docs
    if docs.get("prd"):
        parts.append(f'<a class="doc-link" href="{docs["prd"]}">📄 PRD</a>')
    if docs.get("tech"):
        parts.append(f'<a class="doc-link" href="{docs["tech"]}">📐 Tech Spec</a>')

    # report
    report = task.get("report")
    if report:
        parts.append(f'<a class="doc-link" href="{report}">📊 Report</a>')

    # blocked
    if blocked:
        parts.append(f'<div class="blocked-reason">⚠ {blocked}</div>')

    # notes
    if notes:
        for n in notes[-2:]:
            clean = n.replace("✅ ", "").replace("❌ ", "")
            parts.append(f'<div class="card-desc" style="color:#777">• {clean}</div>')

    parts.append(f'<div class="card-time">created {created} · updated {updated}')
    if assignee:
        parts.append(f' · @{assignee}')
    parts.append(f'</div>')
    parts.append('</div>')
    return '\n'.join(parts)


def render(tasks_path, template_path, output_path):
    with open(tasks_path) as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    with open(template_path) as f:
        template = f.read()

    meta = f'{len(tasks)} tasks · rendered {datetime.now().strftime("%Y-%m-%d %H:%M")}'

    # classify tags: project tags appear in multiple tasks and look like project names
    # heuristic: tags that match a known project or appear as a "grouping" tag
    # we use a simple rule: if the tag == cwd basename of any known project dir, or
    # we just collect all unique tags and let the user decide via data-group
    # For now: auto-detect project tags by checking if tag name matches a directory under ~/Documents/ or ~/Projects/
    home = os.path.expanduser("~")
    known_projects = set()
    for search_dir in ["Documents/lab", "Documents/git-workspace", "Projects"]:
        d = os.path.join(home, search_dir)
        if os.path.isdir(d):
            for name in os.listdir(d):
                if os.path.isdir(os.path.join(d, name)) and not name.startswith('.'):
                    known_projects.add(name)

    # also check tags that look like project names (contain '-', no special chars)
    tag_counter = Counter()
    tag_task_ids = {}
    for t in tasks:
        for tag in t.get("tags", []):
            tag_counter[tag] += 1
            tag_task_ids.setdefault(tag, []).append(t["id"])

    # classify: project tags are those matching known project dirs, or explicitly set
    project_tags = set()
    for tag in tag_counter:
        if tag in known_projects:
            project_tags.add(tag)
    # also: if a tag appears on ALL tasks, it's likely a project tag
    for tag, count in tag_counter.items():
        if count == len(tasks) and len(tasks) > 0:
            project_tags.add(tag)

    # Build 3 filter rows
    # Row 1: Project
    project_filter = f'<div class="filter-row"><span class="filter-label">项目:</span>\n'
    project_filter += f'<span class="filter-tag filter-all active" data-group="project" data-filter="__all__">全部</span>\n'
    for tag in sorted(project_tags):
        count = tag_counter.get(tag, 0)
        project_filter += f'<span class="filter-tag" data-group="project" data-filter="{tag}">{tag} ({count})</span>\n'
    project_filter += '</div>'

    # Row 2: Status
    status_filter = f'<div class="filter-row"><span class="filter-label">状态:</span>\n'
    status_filter += f'<span class="filter-tag filter-all active" data-group="status" data-filter="__all__">全部</span>\n'
    for st in STATUSES:
        count = sum(1 for t in tasks if t.get("status") == st)
        status_filter += f'<span class="filter-tag" data-group="status" data-filter="{st}">{STATUS_LABELS[st]} ({count})</span>\n'
    status_filter += '</div>'

    # Row 3: Tags (non-project, non-priority)
    normal_tags = {k: v for k, v in tag_counter.items() if k not in project_tags}
    tag_filter = f'<div class="filter-row"><span class="filter-label">标签:</span>\n'
    tag_filter += f'<span class="filter-tag filter-all active" data-group="tag" data-filter="__all__">全部</span>\n'
    for tag, count in sorted(normal_tags.items()):
        tag_filter += f'<span class="filter-tag" data-group="tag" data-filter="{tag}">{tag} ({count})</span>\n'
    tag_filter += '</div>'

    # Build columns
    columns = {s: [] for s in STATUSES}
    for t in tasks:
        st = t.get("status", "pending")
        if st not in columns:
            st = "pending"
        columns[st].append(t)

    for st in columns:
        columns[st].sort(key=lambda x: (x.get("priority", "P2"), x["id"]))

    col_html = ""
    for st in STATUSES:
        col_class = f"col-{st}"
        label = STATUS_LABELS[st]
        count = len(columns[st])
        col_html += f'<div class="column {col_class}">\n'
        col_html += f'  <div class="column-header">{label} <span class="count">{count}</span></div>\n'
        col_html += f'  <div class="column-body">\n'
        if columns[st]:
            for t in columns[st]:
                col_html += render_card(t, project_tags) + '\n'
        else:
            col_html += '<div class="empty-col">—</div>\n'
        col_html += '  </div>\n</div>\n'

    html = template
    html = html.replace("__META_LINE__", meta)
    html = html.replace("<!-- __FILTER_PROJECT__ -->", project_filter)
    html = html.replace("<!-- __FILTER_STATUS__ -->", status_filter)
    html = html.replace("<!-- __FILTER_TAGS__ -->", tag_filter)
    html = html.replace("<!-- __BOARD_CONTENT__ -->", col_html)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Rendered {len(tasks)} tasks → {output_path}")
    print(f"  projects: {sorted(project_tags)}")
    print(f"  tags: {sorted(normal_tags.keys())}")


if __name__ == "__main__":
    project_base = os.path.expanduser("~/.project")
    tasks_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(project_base, "tasks.json")
    template_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "board.html")
    output_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(project_base, "board.html")
    render(tasks_path, template_path, output_path)

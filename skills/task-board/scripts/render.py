#!/usr/bin/env python3
"""Render tasks.json → board.html via Jinja2. Data preparation only, no HTML concat."""

import json
import sys
import os
from datetime import datetime
from collections import Counter
from jinja2 import Environment, FileSystemLoader

SKILL_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_BASE = os.path.expanduser("~/.project")

STATUSES = ["pending", "in_progress", "blocked", "done", "cancelled"]
STATUS_LABELS = {
    "pending": "Pending", "in_progress": "In Progress",
    "blocked": "Blocked", "done": "Done", "cancelled": "Cancelled",
}

def fmt_elapsed(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds / 60)}m"
    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    return f"{h}h {m}m" if m else f"{h}h"

def calc_elapsed(task):
    created = task.get("created_at", "")
    if not created:
        return None, None, ""
    try:
        created_dt = datetime.fromisoformat(created)
    except ValueError:
        return None, None, ""

    status = task.get("status", "pending")
    end = None

    if status == "done" and task.get("completed_at"):
        try:
            end = datetime.fromisoformat(task["completed_at"])
        except ValueError:
            pass

    now = datetime.now()
    end_dt = end if end else now
    secs = max(0, (end_dt - created_dt).total_seconds())
    emoji = {"blocked": "🚧", "pending": "⏳", "in_progress": "⏱"}.get(status, "")
    label = f"{emoji} {fmt_elapsed(secs)}" if emoji else fmt_elapsed(secs)
    cls = "elapsed-blocked" if status == "blocked" else ""

    return secs, cls, label


def detect_projects(tasks):
    """Detect project tags: scan known project dirs + tags on all tasks."""
    home = os.path.expanduser("~")
    known = set()

    # Scan common project directories
    for search_dir in [
        "Documents/lab", "Documents/git-workspace", "Projects",
        "Documents", "code", "dev", "workspace", "repos",
    ]:
        d = os.path.join(home, search_dir)
        if os.path.isdir(d):
            for name in os.listdir(d):
                if os.path.isdir(os.path.join(d, name)) and not name.startswith('.'):
                    known.add(name)

    # Collect all tags
    tag_counter = Counter()
    for t in tasks:
        for tag in t.get("tags", []):
            tag_counter[tag] += 1

    # Project tags = tags matching a known dir OR appearing on all tasks
    n = len(tasks) if tasks else 1
    projects = set()
    for tag in tag_counter:
        if tag in known:
            projects.add(tag)
    for tag, count in tag_counter.items():
        if count == n:
            projects.add(tag)

    return projects, tag_counter


def render(tasks_path, template_path, output_path):
    with open(tasks_path) as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    project_tags, tag_counter = detect_projects(tasks)

    # Status counters
    status_counter = Counter()
    for t in tasks:
        status_counter[t.get("status", "pending")] += 1

    # Filter items — show ALL tags that appear in tasks
    filters = {
        "project": [{"name": p, "count": tag_counter[p]} for p in sorted(project_tags)],
        "status": [{"name": s, "label": STATUS_LABELS.get(s, s), "count": status_counter.get(s, 0)} for s in STATUSES],
        "tag": [{"name": t, "count": c} for t, c in sorted(tag_counter.items()) if t not in project_tags],
    }

    # Column grouping
    col_map = {s: [] for s in STATUSES}
    for t in tasks:
        st = t.get("status", "pending")
        if st not in col_map:
            st = "pending"
        col_map[st].append(t)

    columns = []
    for s in STATUSES:
        cards = col_map[s]
        cards.sort(key=lambda x: (0 if x.get("priority") == "P1" else 1 if x.get("priority") == "P2" else 2, x["id"]))
        card_list = []
        for t in cards:
            tags = t.get("tags", [])
            proj_on_card = [tg for tg in tags if tg in project_tags]
            normal_tags = [tg for tg in tags if tg not in project_tags]
            _, elapsed_cls, elapsed_str = calc_elapsed(t)

            card_list.append({
                "id": t["id"],
                "title": t.get("title", ""),
                "description": t.get("description", ""),
                "priority": t.get("priority", "P2"),
                "plevel": t.get("priority", "P2")[1] if t.get("priority") else "2",
                "status": t.get("status", "pending"),
                "project_tags": proj_on_card,
                "normal_tags": normal_tags,
                "tag_str": ",".join(normal_tags),
                "proj_str": ",".join(proj_on_card),
                "docs": t.get("docs", {}),
                "report": t.get("report"),
                "blocked_reason": t.get("blocked_reason"),
                "notes": t.get("notes", []),
                "assignee": t.get("assignee", ""),
                "created": (t.get("created_at", "") or "")[:10] if t.get("created_at") else "",
                "updated": (t.get("updated_at", "") or "")[:10] if t.get("updated_at") else "",
                "elapsed": elapsed_str,
                "elapsed_class": elapsed_cls,
            })

        columns.append({
            "name": s,
            "status": s,
            "label": STATUS_LABELS.get(s, s),
            "count": len(cards),
            "cards": card_list,
        })

    meta = f"{len(tasks)} tasks · {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(os.path.basename(template_path))
    html = tmpl.render(meta=meta, filters=filters, columns=columns)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Rendered {len(tasks)} tasks → {output_path}")
    print(f"  projects: {sorted(project_tags)}")
    print(f"  tags: {sorted(tag_counter.keys() - project_tags)}")


if __name__ == "__main__":
    tasks_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_BASE, "tasks.json")
    template_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SKILL_DIR, "templates", "board.html")
    output_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(PROJECT_BASE, "board.html")
    render(tasks_path, template_path, output_path)

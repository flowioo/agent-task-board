#!/usr/bin/env python3
"""Render task report to HTML."""

import json
import sys
import os
from datetime import datetime

def render_report(tasks_path, task_id, output_path, template_path=None):
    if template_path is None:
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "report.html")

    with open(tasks_path) as f:
        data = json.load(f)

    task = None
    for t in data["tasks"]:
        if t["id"] == task_id:
            task = t
            break

    if not task:
        print(f"Task {task_id} not found")
        sys.exit(1)

    with open(template_path) as f:
        template = f.read()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # replace simple placeholders
    html = template
    html = html.replace("__TASK_ID__", task["id"])
    html = html.replace("__TASK_TITLE__", task.get("title", ""))
    html = html.replace("__DATE__", now)

    # determine result from status
    status = task.get("status", "pending")
    if status == "done":
        html = html.replace("__RESULT__", "PASS")
        html = html.replace("__RESULT_BADGE__", "badge-pass")
    elif status == "blocked":
        html = html.replace("__RESULT__", "BLOCKED")
        html = html.replace("__RESULT_BADGE__", "badge-blocked")
    else:
        html = html.replace("__RESULT__", "N/A")
        html = html.replace("__RESULT_BADGE__", "badge-fail")

    # checks table from notes (lines containing ✅ or ❌)
    notes = task.get("notes", [])
    check_lines = [n for n in notes if "✅" in n or "❌" in n or "checks" in n.lower()]

    checks_html = ""
    if check_lines:
        checks_html = '<div class="section"><h2>Checks</h2><table><tr><th>#</th><th>Item</th><th>Result</th></tr>\n'
        for i, line in enumerate(check_lines, 1):
            if "✅" in line:
                result_cell = '<td class="check-pass">✅ Pass</td>'
                clean = line.replace("✅", "").strip()
            elif "❌" in line:
                result_cell = '<td class="check-fail">❌ Fail</td>'
                clean = line.replace("❌", "").strip()
            else:
                result_cell = f'<td>{line.strip()}</td>'
                clean = ""
            if clean:
                checks_html += f'<tr><td>{i}</td><td>{clean}</td>{result_cell}</tr>\n'
        checks_html += '</table></div>'

    html = html.replace("<!-- __CHECKS_SECTION__ -->", checks_html)

    # flow section
    flow_html = ""
    if status in ("done", "blocked", "cancelled"):
        created = task.get("created_at", "")[:16]
        updated = task.get("updated_at", "")[:16]
        completed = task.get("completed_at", "")
        flow = f"pending({created}) → in_progress → {status}"
        if completed:
            flow += f"({completed[:16]})"
        flow_html = f'<div class="section"><h2>Status Flow</h2><div class="flow">{flow}</div></div>'

    html = html.replace("<!-- __FLOW_SECTION__ -->", flow_html)

    # notes section (non-check notes)
    other_notes = [n for n in notes if n not in check_lines]
    notes_html = ""
    if other_notes:
        notes_html = '<div class="section"><h2>Notes</h2>\n'
        for n in other_notes:
            notes_html += f'<div class="note">{n}</div>\n'
        notes_html += '</div>'

    html = html.replace("<!-- __NOTES_SECTION__ -->", notes_html)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Report rendered → {output_path}")


if __name__ == "__main__":
    project_base = os.path.expanduser("~/.project")
    tasks_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(project_base, "tasks.json")
    task_id = sys.argv[2] if len(sys.argv) > 2 else "T-001"
    output_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(project_base, "reports", f"{task_id}.html")
    template_path = sys.argv[4] if len(sys.argv) > 4 else None
    render_report(tasks_path, task_id, output_path, template_path)

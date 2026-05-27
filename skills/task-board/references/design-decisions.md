# Task Board Design Decisions

## Architecture Evolution

### v0.1: Per-project directories
- `~/.project/{name}/.tasks/tasks.json` — each project had its own file
- Required `resolve_project()` logic, overview.html for cross-project view
- Problem: overhead for few projects, complex path resolution

### v0.2 → v0.3: Single file + tag-based projects
- `~/.project/tasks.json` — all tasks in one file
- Project = a tag (cwd basename auto-appended)
- board.html's 3-row filter handles project isolation
- overview.html eliminated — board IS the overview
- Global T-NNN numbering (no per-project sequences)

Key insight: With few projects (< 10) and modest task counts (< 100), single-file JSON + tag filtering beats directory-based isolation. Simpler code, simpler paths, no resolve_project needed.

## Path Convention

board.html lives at `~/.project/board.html`. All relative links resolve from there:
- `reports/T-NNN.html` — report files
- `docs/xxx.md` — associated documents

Do NOT prefix with `.tasks/` — that was the old per-project structure.

## Visual Design (v0.3 — taste-skill informed)

Applied principles from taste-skill:
- **Zinc palette**: bg #09090b → #18181b, border #27272a → #2e2e32
- **Single accent**: emerald (#10b981) only — no purple, no rainbow
- **Typography**: Inter for body, JetBrains Mono for metadata/IDs
- **Radius lock**: 8px cards, 6px small elements, pill for tags — one system
- **No emoji in links**: doc-link text is plain (no 📄📊 emoji prefix)
- **Consistent borders**: subtle 1px, tinted to background hue
- **Card hover**: border-color + background shift, no transform/scale

## State Machine

```
pending → in_progress → done       (terminal)
   │           │
   │           ↓
   └──→ blocked → in_progress
   │
   └──→ cancelled                 (terminal)
```

- done/cancelled are terminal — cannot transition out
- blocked is recoverable → in_progress or cancelled
- blocked requires blocked_reason (non-empty string)
- done requires completed_at (ISO timestamp)

## Data Model

```json
{
  "next_id": 8,
  "tasks": [{
    "id": "T-001",
    "title": "...",
    "description": "...",
    "status": "pending|in_progress|blocked|done|cancelled",
    "priority": "P1|P2|P3",
    "tags": ["cc", "backend"],
    "docs": { "prd": "docs/prd-xxx.md", "tech": "docs/tech-xxx.md" },
    "notes": ["decision log entries"],
    "report": "reports/T-001.html",
    "blocked_reason": null,
    "created_at": "2026-05-26T...",
    "updated_at": "2026-05-26T...",
    "completed_at": null
  }]
}
```

## Filter Design

Three rows, AND between rows, OR within a row:
1. Project row (green accent) — filter by project tag
2. Status row (amber accent) — filter by status
3. Tag row (blue accent) — filter by non-project tags

"ALL" button per row resets that row's filter.
Column counts update to show `visible/total` when filtered.

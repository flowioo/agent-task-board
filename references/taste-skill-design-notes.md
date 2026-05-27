# Taste-Skill Design Principles (Applied to Task Board)

Source: github.com/Leonxlnx/taste-skill — Anti-slop frontend design skill.

Key principles applied to board.html and report.html:

## Color
- Single accent color (emerald #10b981), saturation controlled
- No AI-purple gradients, no neon. Zinc/slate neutrals only
- One palette per project. Consistent hue-tinted shadows

## Typography
- Inter for body, JetBrains Mono for data/IDs
- Don't default to serif. Sans-serif display for functional UIs
- Monospace for metadata (IDs, timestamps, counts)

## Shape
- ONE corner-radius scale: 8px cards, 6px small, pill for tags/buttons
- No mixed radius systems without documented rule

## Layout
- Cards only when elevation communicates hierarchy
- Negative space > borders > cards for grouping
- Filter rows: compact pill buttons, grouped by category

## Motion
- Minimal for tool UIs (MOTION_INTENSITY ~2): hover states, subtle transitions
- No infinite loops, no gratuitous animations on data-dense interfaces
- 0.12s ease transitions for state changes

## Anti-Patterns (from taste-skill)
- Don't center everything. Left-aligned is fine for data boards
- Don't add eyebrows/labels above every section header
- Don't use emoji as UI elements in professional tools
- No div-based fake UI. Real data, real cards

## Visual Density
- Task board: DENSITY ~5 (data board, not art gallery)
- Cards compact but scannable: 12px padding, 13px titles
- Mono-spaced metadata in muted colors to reduce visual noise

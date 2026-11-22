"""Append accepted ideas from the Mark 1 Feature Ideas board to docs/mark1-features.xlsx.

Usage: python3 scripts/add_accepted_ideas.py accepted.json [docs/mark1-features.xlsx]

accepted.json is a JSON list of idea objects as stored in the board's `ideas`
collection, each with an "id" field plus title, description, effort, ai,
section, competitor. Ideas whose ID (I-<idea id>) is already in the Features
sheet are skipped, so the script is safe to run every day.
"""
import json
import sys

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, PatternFill, Side

src = sys.argv[1]
xlsx = sys.argv[2] if len(sys.argv) > 2 else "docs/mark1-features.xlsx"

ideas = json.load(open(src))
wb = load_workbook(xlsx)
ws = wb["Features"]
existing = {ws.cell(r, 1).value for r in range(2, ws.max_row + 1)}
thin = Side(style="thin", color="D0D7DE")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
fill = PatternFill("solid", fgColor="FFF4CC")

added = 0
for idea in ideas:
    fid = f"I-{idea['id']}"
    if fid in existing:
        continue
    origin = (
        f"From competitor: {idea.get('competitor', '')}"
        if idea.get("section") == "competitor"
        else "Original idea"
    )
    ws.append([
        fid,
        idea.get("title", ""),
        "Idea backlog",
        idea.get("description", ""),
        "",
        "Should",
        "Backlog",
        idea.get("effort", ""),
        "Yes" if idea.get("ai") else "No",
        "",
        "Agreed",
        "",
        f"{origin}. Accepted {idea.get('decidedAt', '')[:10]}. Why: {idea.get('whyItMatters', '')}",
    ])
    row = ws.max_row
    for c in ws[row]:
        c.alignment = Alignment(vertical="top", wrap_text=True)
        c.border = border
    ws[f"G{row}"].fill = fill
    added += 1

ws.auto_filter.ref = ws.dimensions
wb.save(xlsx)
print(f"added {added} idea(s)")

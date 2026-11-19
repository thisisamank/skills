"""Render the traffic ceiling report as one self-contained HTML file.

usage: python3 report.py report.json out.html

report.json shape (see ../references/report-example.json):
{
  "title": "...", "subtitle": "...", "date": "YYYY-MM-DD",
  "summary": ["one sentence", "..."],
  "sections": [
    {"heading": "...", "paragraphs": ["..."], "table": {"columns": [...], "rows": [[...]]},
     "bullets": ["..."], "numbered": ["..."], "note": "..."}
  ]
}
Every key inside a section is optional. Sections render in order.
"""
import html
import json
import sys

CSS = """
:root { --bg: #ffffff; --fg: #1a1a1a; --muted: #5f6368; --line: #e3e3e3; --accent: #1a56db; --soft: #f4f6fb; }
@media (prefers-color-scheme: dark) { :root { --bg: #111214; --fg: #ececec; --muted: #9aa0a6; --line: #2c2e33; --accent: #8ab4f8; --soft: #1b1d22; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
main { max-width: 880px; margin: 0 auto; padding: 48px 16px 96px; }
h1 { font-size: 2rem; line-height: 1.2; margin: 0 0 4px; }
h2 { font-size: 1.35rem; margin: 48px 0 12px; padding-top: 24px; border-top: 1px solid var(--line); }
p { margin: 0 0 12px; }
.sub { color: var(--muted); margin-bottom: 24px; }
.summary { background: var(--soft); border-radius: 10px; padding: 16px 20px; margin: 24px 0 8px; }
.summary p { margin: 0 0 8px; }
.summary p:last-child { margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 12px 0 16px; font-size: 0.95rem; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.02em; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.wrap { overflow-x: auto; }
ul, ol { padding-left: 22px; margin: 0 0 12px; }
li { margin: 0 0 6px; }
.note { color: var(--muted); font-size: 0.9rem; }
code { background: var(--soft); padding: 1px 5px; border-radius: 4px; font-size: 0.9em; }
"""


def esc(s):
    return html.escape(str(s))


def is_num(v):
    s = str(v).replace(",", "").replace("$", "").replace("%", "").replace("about ", "").strip()
    return s.replace(".", "", 1).isdigit() or " to " in str(v) and any(ch.isdigit() for ch in str(v))


def table(t):
    cols = t["columns"]
    head = "".join(f"<th{' class=num' if i and all(is_num(r[i]) for r in t['rows'] if i < len(r)) else ''}>{esc(c)}</th>" for i, c in enumerate(cols))
    body = ""
    for r in t["rows"]:
        body += "<tr>" + "".join(f"<td{' class=num' if i and is_num(v) else ''}>{esc(v)}</td>" for i, v in enumerate(r)) + "</tr>"
    return f'<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def section(s):
    out = [f"<h2>{esc(s['heading'])}</h2>"]
    for p in s.get("paragraphs", []):
        out.append(f"<p>{esc(p)}</p>")
    if "table" in s:
        out.append(table(s["table"]))
    if s.get("bullets"):
        out.append("<ul>" + "".join(f"<li>{esc(b)}</li>" for b in s["bullets"]) + "</ul>")
    if s.get("numbered"):
        out.append("<ol>" + "".join(f"<li>{esc(b)}</li>" for b in s["numbered"]) + "</ol>")
    if s.get("note"):
        out.append(f'<p class="note">{esc(s["note"])}</p>')
    return "\n".join(out)


def render(r):
    summary = "".join(f"<p>{esc(p)}</p>" for p in r.get("summary", []))
    body = "\n".join(section(s) for s in r["sections"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(r['title'])}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>{esc(r['title'])}</h1>
<p class="sub">{esc(r.get('subtitle', ''))} {('· ' + esc(r['date'])) if r.get('date') else ''}</p>
<div class="summary">{summary}</div>
{body}
</main>
</body>
</html>
"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    spec = json.load(open(sys.argv[1]))
    open(sys.argv[2], "w").write(render(spec))
    print("wrote", sys.argv[2])

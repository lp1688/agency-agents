#!/usr/bin/env python3
"""Generate agents-catalog.html: all Agency agents grouped by division.

Usage: python scripts/gen-html-catalog.py [--lang zh-TW]
With --lang zh-TW, translations from i18n_chunks/*.zh-TW.json are applied and
the output is agents-catalog.zh-TW.html.
"""
import argparse
import json
import re
import html
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("--lang", default="en")
args = parser.parse_args()
ZH = args.lang == "zh-TW"

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / ("agents-catalog.zh-TW.html" if ZH else "agents-catalog.html")

divisions = json.loads((ROOT / "divisions.json").read_text(encoding="utf-8"))["divisions"]

translations = {}
if ZH:
    for f in sorted((ROOT / "i18n_chunks").glob("*.zh-TW.json")):
        for item in json.loads(f.read_text(encoding="utf-8")):
            translations[item["key"]] = item

DIV_ZH = {
    "academic": "學術", "design": "設計", "engineering": "工程", "finance": "財務",
    "game-development": "遊戲開發", "gis": "GIS", "healthcare": "醫療保健",
    "marketing": "行銷", "paid-media": "付費媒體", "product": "產品",
    "project-management": "專案管理", "research": "研究", "sales": "銷售",
    "security": "資安",
    "spatial-computing": "空間運算", "specialized": "專業領域",
    "support": "支援", "testing": "測試",
}

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

def parse_agent(path):
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta

sections = []
total = 0
for slug, info in divisions.items():
    d = ROOT / slug
    if not d.is_dir():
        continue
    agents = []
    for f in sorted(d.rglob("*.md")):
        meta = parse_agent(f)
        if not meta.get("name"):
            continue
        # Sub-group for nested dirs (e.g. game-development/unity)
        meta["_group"] = f.parent.name if f.parent != d else ""
        t = translations.get(f.stem)
        if t:
            meta["_name_en"] = meta["name"]
            meta["name"] = t["name"]
            meta["vibe"] = t["vibe"]
            meta["description"] = t["description"]
        agents.append(meta)
    total += len(agents)
    sections.append((slug, info, agents))

def esc(s):
    return html.escape(s or "", quote=True)

cards_css = ""
parts = []
for slug, info, agents in sections:
    label = esc(DIV_ZH[slug] if ZH else info["label"])
    color = info["color"]
    cards = []
    last_group = None
    for a in agents:
        if a["_group"] != last_group:
            last_group = a["_group"]
            if last_group:
                cards.append(f'<div class="group-label">{esc(last_group)}</div>')
        search_text = a.get('name','') + ' ' + a.get('description','') + ' ' + a.get('_name_en','')
        name_en = f'<span class="name-en">{esc(a["_name_en"])}</span>' if ZH and a.get("_name_en") else ""
        cards.append(
            f'''<div class="card" data-search="{esc(search_text.lower())}">
  <div class="card-head"><span class="emoji">{esc(a.get('emoji','🎭'))}</span><span class="name">{esc(a.get('name'))}</span>{name_en}</div>
  <div class="vibe">{esc(a.get('vibe',''))}</div>
  <div class="desc">{esc(a.get('description',''))}</div>
</div>'''
        )
    parts.append(
        f'''<section id="{slug}">
<h2 style="border-left:6px solid {color}">{label} <span class="count">{len(agents)}</span></h2>
<div class="grid">{''.join(cards)}</div>
</section>'''
    )

toc = "".join(
    f'<a href="#{slug}" style="border-left:4px solid {info["color"]}">{esc(DIV_ZH[slug] if ZH else info["label"])} <span class="toc-count">{len(agents)}</span></a>'
    for slug, info, agents in sections
)

if ZH:
    title = f"The Agency — AI 專家目錄（{total} 個 agents）"
    subtitle = f"{total} 個專業 agents · {len(sections)} 個部門 · 來源："
    footer_text = "由每個 agent 原始 .md 檔的 frontmatter 產生，繁體中文為 AI 翻譯。每個 agent 安裝於 <code>~/.config/kimi/agents/&lt;agent-name&gt;/</code>。"
else:
    title = f"The Agency — Agents Catalog ({total} agents)"
    subtitle = f"{total} specialized agents · {len(sections)} divisions · source: "
    footer_text = "Generated from frontmatter of each agent's source .md file. Each agent installs to <code>~/.config/kimi/agents/&lt;agent-name&gt;/</code>."

page = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Segoe UI", "Microsoft JhengHei", sans-serif; margin:0; background:#0f1115; color:#e5e7eb; }}
  header {{ padding:32px 40px 16px; background:#161922; border-bottom:1px solid #262b38; position:sticky; top:0; z-index:10; }}
  header h1 {{ margin:0 0 4px; font-size:24px; }}
  header p {{ margin:0 0 12px; color:#9ca3af; font-size:14px; }}
  #search {{ width:100%; max-width:480px; padding:10px 14px; border-radius:8px; border:1px solid #374151; background:#0f1115; color:#e5e7eb; font-size:15px; }}
  #search:focus {{ outline:2px solid #3b82f6; }}
  .wrap {{ display:flex; }}
  nav {{ width:220px; flex-shrink:0; padding:24px 16px; position:sticky; top:150px; align-self:flex-start; max-height:calc(100vh - 150px); overflow:auto; }}
  nav a {{ display:block; padding:8px 12px; margin-bottom:4px; color:#d1d5db; text-decoration:none; border-radius:6px; font-size:14px; }}
  nav a:hover {{ background:#1f2430; color:#fff; }}
  .toc-count {{ float:right; color:#6b7280; font-size:12px; }}
  main {{ flex:1; padding:24px 40px 80px; min-width:0; }}
  section {{ margin-bottom:48px; }}
  h2 {{ padding:6px 14px; font-size:20px; margin:0 0 16px; }}
  .count {{ color:#6b7280; font-size:14px; font-weight:normal; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; }}
  .group-label {{ grid-column:1/-1; color:#6b7280; font-size:13px; text-transform:uppercase; letter-spacing:.08em; margin-top:6px; }}
  .card {{ background:#161922; border:1px solid #262b38; border-radius:10px; padding:14px 16px; }}
  .card:hover {{ border-color:#3b82f6; }}
  .card-head {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
  .emoji {{ font-size:20px; }}
  .name {{ font-weight:600; font-size:15px; }}
  .name-en {{ color:#6b7280; font-size:12px; font-weight:normal; }}
  .vibe {{ color:#93c5fd; font-size:12.5px; font-style:italic; margin-bottom:8px; }}
  .desc {{ color:#9ca3af; font-size:13.5px; line-height:1.55; }}
  .hidden {{ display:none !important; }}
  footer {{ padding:24px 40px; color:#6b7280; font-size:13px; border-top:1px solid #262b38; }}
  @media (max-width:800px) {{ nav {{ display:none; }} header {{ padding:20px; }} main {{ padding:20px; }} }}
</style>
</head>
<body>
<header>
  <h1>🎭 {title}</h1>
  <p>{subtitle}<a style="color:#93c5fd" href="https://github.com/msitarzewski/agency-agents">msitarzewski/agency-agents</a></p>
  <input id="search" type="search" placeholder="搜尋 agent 名稱或說明… (e.g. react, 資安, 小紅書)">
</header>
<div class="wrap">
<nav>{toc}</nav>
<main>{''.join(parts)}</main>
</div>
<footer>{footer_text}</footer>
<script>
const input = document.getElementById('search');
input.addEventListener('input', () => {{
  const q = input.value.trim().toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    c.classList.toggle('hidden', q && !c.dataset.search.includes(q));
  }});
  document.querySelectorAll('section').forEach(s => {{
    const visible = s.querySelectorAll('.card:not(.hidden)').length;
    s.classList.toggle('hidden', q && !visible);
  }});
}});
</script>
</body>
</html>'''

OUT.write_text(page, encoding="utf-8")
print(f"Wrote {OUT} ({total} agents, {len(sections)} divisions)")

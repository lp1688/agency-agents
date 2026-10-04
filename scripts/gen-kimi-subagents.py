#!/usr/bin/env python3
"""Install Agency agents as Kimi Code custom (sub-)agents.

Converts every division's source .md into the Markdown agent format that
Kimi Code CLI discovers (https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html):

- frontmatter `name` becomes kebab-case (file stem minus the division prefix);
  Kimi Code skips files whose name is not kebab-case
- `description` is kept verbatim so the main Agent can route delegations
- a handoff note is appended so delegated runs return a self-contained result

Usage: python scripts/gen-kimi-subagents.py [--dest DIR]
Default dest: $KIMI_CODE_HOME/agents or ~/.kimi-code/agents
"""
import argparse
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--dest", default=None)
args = parser.parse_args()

if args.dest:
    DEST = pathlib.Path(args.dest).expanduser()
else:
    home = os.environ.get("KIMI_CODE_HOME") or str(pathlib.Path.home() / ".kimi-code")
    DEST = pathlib.Path(home) / "agents"

divisions = json.loads((ROOT / "divisions.json").read_text(encoding="utf-8"))["divisions"]

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

HANDOFF_NOTE = """
---

When delegated as a sub-agent, your final message is the entire handoff: make it a
complete, self-contained result for the caller — findings, decisions, and any
artifacts you created (with file paths).
"""

def parse_agent(path):
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    meta, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = text[m.end():]
    return meta, body

# First pass: collect (short_name, division, path) and detect collisions
entries = []
for slug in divisions:
    d = ROOT / slug
    if not d.is_dir():
        continue
    for f in sorted(d.rglob("*.md")):
        meta, _ = parse_agent(f)
        if not meta.get("description"):
            continue
        short = f.stem
        # Strip the division prefix only when the remainder stays multi-word;
        # a bare generic word (sre, coach, manager) is worse for routing
        remainder = short[len(slug) + 1:]
        if short.startswith(slug + "-") and "-" in remainder:
            short = remainder
        entries.append((short, slug, f))

counts = {}
for short, _, _ in entries:
    counts[short] = counts.get(short, 0) + 1

DEST.mkdir(parents=True, exist_ok=True)
# Remove files from a previous run of this script (identified by the handoff note)
for old in DEST.glob("*.md"):
    if "your final message is the entire handoff" in old.read_text(encoding="utf-8", errors="ignore"):
        old.unlink()
written = 0
for short, slug, f in entries:
    name = short if counts[short] == 1 else f"{slug}-{short}"
    meta, body = parse_agent(f)
    # json.dumps yields a YAML-safe double-quoted scalar
    desc = json.dumps(meta["description"], ensure_ascii=False)
    out = f"---\nname: {name}\ndescription: {desc}\n---\n{body.rstrip()}\n{HANDOFF_NOTE}"
    (DEST / f"{name}.md").write_text(out, encoding="utf-8")
    written += 1

collisions = sorted(s for s, c in counts.items() if c > 1)
print(f"Wrote {written} agents to {DEST}")
if collisions:
    print("Name collisions (kept division prefix):", ", ".join(collisions))

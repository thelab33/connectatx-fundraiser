#!/usr/bin/env python3
"""
Starforge CSS Converge — fold fc-prestige-unified.css into input.css safely.
- Prefers rules already present in input.css
- Preserves at-rules (media/supports/keyframes)
- Writes backups with timestamps
"""

import re, shutil, sys, time
from pathlib import Path

ROOT = Path("app/static/css").resolve()
INPUT = ROOT / "input.css"
PRESTIGE = ROOT / "fc-prestige-unified.css"
STAMP = time.strftime("%Y%m%d-%H%M%S")

if not INPUT.exists() or not PRESTIGE.exists():
    sys.exit(f"Missing files. Need:\n  {INPUT}\n  {PRESTIGE}")

# Backups
shutil.copy2(INPUT, ROOT / f"input.css.bak-{STAMP}")
shutil.copy2(PRESTIGE, ROOT / f"fc-prestige-unified.css.bak-{STAMP}")

src_input = INPUT.read_text(encoding="utf-8")
src_prestige = PRESTIGE.read_text(encoding="utf-8")

# Rough parser for top-level rules (not a full CSS parser, but good enough
# for our structured files: no nested rules except inside @media blocks)
rule_re = re.compile(r"""
    (?P<at>@(?:media|supports|keyframes)[\s\S]*?\{[\s\S]*?\})  # whole at-rule block
    |                                                         # or
    (?P<rule>^[^{@][^{]+?\{[\s\S]*?\})                        # simple top-level rule
""", re.MULTILINE | re.VERBOSE)

# Build selector set from input.css (only simple rules, not at-rules)
existing_selectors = set()
for m in rule_re.finditer(src_input):
    if m.group("rule"):
        selector = m.group("rule").split("{",1)[0].strip()
        existing_selectors.add(selector)

merged_tail = []
skipped = []
added = []
kept_at_blocks = 0

for m in rule_re.finditer(src_prestige):
    block = m.group(0)
    if m.group("at"):
        merged_tail.append(block)
        kept_at_blocks += 1
        continue
    selector = m.group("rule").split("{",1)[0].strip()
    # Skip known duplicates or anything already in input.css
    if selector in existing_selectors:
        skipped.append(selector)
        continue
    merged_tail.append(block)
    added.append(selector)

tail_text = "\n\n/* === Merged from fc-prestige-unified.css @ {} === */\n".format(STAMP)
tail_text += "\n".join(merged_tail) + "\n/* === End merged === */\n"

INPUT.write_text(src_input.rstrip() + "\n\n" + tail_text, encoding="utf-8")

print("✔ Merge complete.")
print(f"  Kept at-rule blocks: {kept_at_blocks}")
print(f"  New simple rules added: {len(added)}")
if added:
    print("  e.g.", ", ".join(added[:8]) + (" ..." if len(added) > 8 else ""))
print(f"  Skipped (already present): {len(skipped)}")
sys.exit(0)


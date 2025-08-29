from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIRS = [
    ROOT / "app" / "templates",
    ROOT / "fundchamps" / "app" / "templates",  # if present
]

# Match: <script ...> with NO src= and NO nonce=
pat = re.compile(r'(<script(?![^>]*\bsrc=)(?![^>]*\bnonce=)[^>]*>)', re.IGNORECASE)

def patch_file(p: Path) -> bool:
    s = p.read_text(encoding="utf-8", errors="ignore")
    new = pat.sub(lambda m: m.group(1)[:-1] + ' nonce="{{ NONCE }}">', s)
    if new != s:
        p.write_text(new, encoding="utf-8")
        return True
    return False

changed = 0
for d in CANDIDATE_DIRS:
    if not d.exists():
        continue
    for p in d.rglob("*.html"):
        if patch_file(p):
            changed += 1

print(f"✅ Patched {changed} file(s)")


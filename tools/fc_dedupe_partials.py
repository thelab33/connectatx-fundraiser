#!/usr/bin/env python3
import re, time, pathlib
TEMPL_DIR = pathlib.Path("app/templates")
INC = re.compile(r'{%\s*include\s+["\'](partials/[^"\']+)["\']\s*%}')
STAMP = time.strftime("%Y%m%d-%H%M%S")

def scan_and_fix(apply=False):
    dupes = {}
    for p in TEMPL_DIR.rglob("*.html"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        hits = INC.findall(txt)
        if not hits: continue
        counts = {}
        for h in hits: counts[h] = counts.get(h,0)+1
        over = [k for k,v in counts.items() if v>1]
        if over:
            dupes[str(p)] = [(k, counts[k]) for k in over]
            if apply:
                lines = txt.splitlines(True)
                seen = {}
                changed = False
                for i,l in enumerate(lines):
                    m = INC.search(l)
                    if not m: continue
                    inc = m.group(1)
                    seen[inc] = seen.get(inc,0)+1
                    if seen[inc] > 1:
                        lines[i] = f'{{# DEDUP {inc} {STAMP} #}} ' + l.replace("{%", "{# %").replace("%}", "% #}")
                        changed = True
                if changed:
                    bak = p.with_suffix(p.suffix + f".{STAMP}.bak")
                    p.replace(bak)
                    p.write_text("".join(lines), encoding="utf-8")
                    print(f"  • Edited {p} (backup at {bak})")
    return dupes

if __name__ == "__main__":
    d = scan_and_fix(apply=False)
    if not d:
        print("✅ No per-file duplicate partial includes found.")
    else:
        print("⚠️  Duplicates detected:")
        for fp, rows in d.items():
            for inc, n in rows:
                print(f"  - {fp}: {inc} ×{n}")
        print("\nRun: python3 tools/fc_dedupe_partials.py --apply to comment extras.")

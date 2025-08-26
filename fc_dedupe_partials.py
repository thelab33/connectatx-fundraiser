#!/usr/bin/env python3
import re, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (adjust if needed)
TEMPL_DIR = ROOT / "app" / "templates"

INC_RX = re.compile(r'{%\s*include\s+["\'](partials/[^"\']+)["\']\s*%}')
STAMP = time.strftime("%Y%m%d-%H%M%S")

def scan():
    dupes = {}
    for p in TEMPL_DIR.rglob("*.html"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        hits = INC_RX.findall(txt)
        if not hits: continue
        seen = {}
        for inc in hits:
            seen.setdefault(inc, 0)
            seen[inc] += 1
        for inc, count in seen.items():
            if count > 1:
                dupes.setdefault(p, []).append((inc, count))
    return dupes

def apply_dedupe(file_path: pathlib.Path):
    lines = file_path.read_text(encoding="utf-8").splitlines(True)
    counts = {}
    changed = False
    for i, line in enumerate(lines):
        m = INC_RX.search(line)
        if not m: continue
        inc = m.group(1)
        counts[inc] = counts.get(inc, 0) + 1
        if counts[inc] > 1:
            # comment out duplicates
            lines[i] = f'{{# DEDUP {inc} {STAMP} #}} ' + line.replace("{%", "{# %").replace("%}", "% #}")
            changed = True
    if changed:
        bak = file_path.with_suffix(file_path.suffix + f".{STAMP}.bak")
        file_path.replace(bak)
        file_path.write_text("".join(lines), encoding="utf-8")
        return str(bak)
    return None

def main():
    apply = "--apply" in sys.argv
    dupes = scan()
    if not dupes:
        print("✅ No per-file duplicate partial includes found.")
        return
    print("⚠️  Duplicates detected:")
    for p, rows in dupes.items():
        for inc, count in rows:
            print(f"  - {p}: {inc} ×{count}")
    if apply:
        print("\n✍️  Applying dedupe (commenting duplicates, keeping first)…")
        for p in dupes:
            bak = apply_dedupe(p)
            if bak:
                print(f"  • Edited {p} (backup at {bak})")
        print("✅ Done. Review git diff and test.")
    else:
        print("\n(run with --apply to comment extra copies)")

if __name__ == "__main__":
    main()


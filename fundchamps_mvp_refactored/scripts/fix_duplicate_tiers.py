
#!/usr/bin/env python3
import sys, re, pathlib, argparse

PATTERN = re.compile(r"<section\s+id=["']tiers["'][\s\S]*?</section>", re.IGNORECASE)

def scan(path: pathlib.Path, write: bool):
    text = path.read_text(encoding='utf-8', errors='ignore')
    matches = list(PATTERN.finditer(text))
    if len(matches) <= 1:
        return False, 0
    # keep first, remove others
    new = text[:matches[0].end()]
    cursor = matches[0].end()
    removed = 0
    for m in matches[1:]:
        removed += 1
        # insert a comment marker where it was
        new += text[cursor:m.start()] + "{# removed duplicate <section id='tiers'> (use macros/tiers.html) #}"
        cursor = m.end()
    new += text[cursor:]
    if write:
        path.write_text(new, encoding='utf-8')
    return True, removed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="templates root or file")
    ap.add_argument("--write", action="store_true", help="apply fixes in-place")
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    files = []
    if root.is_file():
        files = [root]
    else:
        files = [p for p in root.rglob("*.html")]
    total_removed = 0
    changed = 0
    for f in files:
        did, rem = scan(f, args.write)
        if did:
            changed += 1
            total_removed += rem
            print(f"[fix-dup] {f} -> removed {rem} duplicate(s)")
    if not changed:
        print("[fix-dup] no duplicates found")
    else:
        print(f"[fix-dup] changed {changed} file(s), removed {total_removed} duplicate block(s)")
if __name__ == "__main__":
    main()

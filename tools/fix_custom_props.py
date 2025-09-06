#!/usr/bin/env python3
import argparse, re, sys
from pathlib import Path

# Files we will scan by default (edit as needed)
DEFAULT_GLOBS = [
    "app/static/css/**/*.css",
    "app/templates/**/*.*",
    "app/**/*.js",
    "frontend/**/*.js",
    "frontend/**/*.ts",
    "frontend/**/*.tsx",
]

# find all --tokens in CSS/HTML/JS contexts:
#   --FooBar, --_FooBar, --imgX, etc.
TOKEN_RE = re.compile(r"--([A-Za-z0-9_][A-Za-z0-9_-]*)")

# JS property string patterns: '--FooBar' inside quotes for setProperty/getPropertyValue, etc.
JS_PROP_STRING_RE = re.compile(r"(['\"])--([A-Za-z0-9_][A-Za-z0-9_-]*)\1")

def to_kebab(name: str) -> str:
    # keep leading '_' private marker intact, but kebab-case the rest
    if name.startswith("_"):
        return "_" + _kebab(name[1:])
    return _kebab(name)

def _kebab(s: str) -> str:
    # turn camelCase/PascalCase/snake_case to kebab-case
    s = s.replace("__", "_")
    # convert camelCase: abcDef -> abc-Def
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    # snake_case -> snake-case
    s = s.replace("_", "-")
    # collapse multiple dashes, lower
    s = re.sub(r"-{2,}", "-", s)
    return s.lower()

def rewrite_tokens(text: str) -> tuple[str, dict]:
    """
    Rewrites:
      --FooBar -> --foo-bar
      var(--FooBar) -> var(--foo-bar)
      '--FooBar' in JS -> '--foo-bar'
    Returns (new_text, mapping_counts)
    """
    mapping_counts = {}

    # First pass: rewrite raw --tokens
    def token_repl(m: re.Match):
        orig = m.group(0)            # e.g. --FooBar
        body = m.group(1)            # FooBar
        keb = to_kebab(body)
        new = f"--{keb}"
        if new != orig:
            mapping_counts[(orig, new)] = mapping_counts.get((orig, new), 0) + 1
        return new

    text = TOKEN_RE.sub(token_repl, text)

    # Second pass: fix JS string literals '--FooBar'
    def js_repl(m: re.Match):
        quote = m.group(1)
        body  = m.group(2)
        keb = to_kebab(body)
        orig_full = f"{quote}--{body}{quote}"
        new_full  = f"{quote}--{keb}{quote}"
        if new_full != orig_full:
            mapping_counts[(orig_full, new_full)] = mapping_counts.get((orig_full, new_full), 0) + 1
        return new_full

    text = JS_PROP_STRING_RE.sub(js_repl, text)
    return text, mapping_counts

def iter_files(globs):
    for g in globs:
        for p in Path(".").glob(g):
            if p.is_file():
                yield p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run preview only)")
    ap.add_argument("--glob", action="append", help="Add an extra glob (may repeat)")
    args = ap.parse_args()

    globs = DEFAULT_GLOBS[:]
    if args.glob:
        globs += args.glob

    total_changes = 0
    mapping_totals = {}

    for f in iter_files(globs):
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue

        new, m = rewrite_tokens(src)
        if new != src:
            total_changes += 1
            # merge counts
            for k, v in m.items():
                mapping_totals[k] = mapping_totals.get(k, 0) + v

            if args.apply:
                bak = f.with_suffix(f.suffix + ".bak")
                if not bak.exists():
                    bak.write_text(src, encoding="utf-8")
                f.write_text(new, encoding="utf-8")

    if mapping_totals:
        print("→ Proposed remaps (orig → new : count):")
        # show a condensed summary
        shown = 0
        for (orig, new), cnt in sorted(mapping_totals.items(), key=lambda x: (-x[1], x[0][0])):
            print(f"   {orig}  →  {new}   ×{cnt}")
            shown += 1
            if shown >= 80:
                print("   … (truncated)")
                break
    else:
        print("• No non-kebab custom properties found. (Or already normalized.)")

    if args.apply:
        print(f"\n✅ Applied changes to {total_changes} file(s). Backups: *.bak")
    else:
        print(f"\n👀 Dry-run complete. Files that would change: {total_changes}. Re-run with --apply to write.")

if __name__ == "__main__":
    main()


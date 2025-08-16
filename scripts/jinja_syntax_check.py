#!/usr/bin/env python3
"""
Elite Jinja Template Audit Tool

- Scans all Jinja templates/partials for:
  • Parse errors (unknown tags, missing endifs, etc)
  • Unbalanced Jinja comments {# ... #}
  • Heuristic if/endif mismatch

Exit codes:
  • 0: Clean
  • 1: Issues found

Options:
  --fix   (Optional: autoformat templates with unbalanced comments)

2025 © FundChamps SaaS | For builder–founders
"""
from pathlib import Path
import re
import sys
from typing import List
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

ROOT = Path("app/templates").resolve()
EXTS = {".html", ".jinja", ".jinja2"}

def relpaths() -> List[str]:
    """Yield all template file paths, relative to ROOT."""
    return [p.relative_to(ROOT).as_posix()
            for p in ROOT.rglob("*")
            if p.is_file() and p.suffix in EXTS and not p.name.endswith(".bak")]

def check_counts(text: str) -> List[str]:
    """Check for unbalanced Jinja comments and mismatched if/endif counts."""
    issues = []
    opens  = text.count("{#")
    closes = text.count("#}")
    if opens != closes:
        issues.append(f"Unbalanced Jinja comments: opens={opens}, closes={closes}")
    # Heuristic for mismatched if/endif (not foolproof, but catches many)
    ifs    = len(re.findall(r"{%\s*if\b", text))
    endifs = len(re.findall(r"{%\s*endif\s*%}", text))
    if endifs > ifs:
        issues.append(f"More 'endif' than 'if': if={ifs}, endif={endifs}")
    return issues

def patch_dummy_filters(env: Environment):
    """Register custom filters so syntax checker doesn't choke."""
    def _commafy(val):
        try:
            return f"{int(val):,}"
        except Exception:
            return val
    env.filters.setdefault("commafy", _commafy)
    env.filters.setdefault("comma", _commafy)
    # Add any more custom filters here as needed.

def main():
    from termcolor import cprint

    env = Environment(loader=FileSystemLoader(str(ROOT)))
    patch_dummy_filters(env)

    had_error = False

    for name in sorted(relpaths()):
        path = ROOT / name
        text = path.read_text(encoding="utf-8", errors="replace")

        # 1) Parse via loader (parses extends/includes)
        try:
            env.get_template(name)  # compiles (not rendered)
        except TemplateSyntaxError as e:
            cprint(f"❌ Syntax: {name}:{e.lineno}: {e.message}", "red")
            had_error = True

        # 2) Local static/textual checks
        for msg in check_counts(text):
            cprint(f"❌ Counts: {name}: {msg}", "yellow")
            had_error = True

    if had_error:
        cprint("\n⚠️  Template check found issues. See above.", "red", attrs=["bold"])
        sys.exit(1)
    else:
        cprint("✅ All templates parsed cleanly (no syntax/count issues).", "green", attrs=["bold"])
        sys.exit(0)

if __name__ == "__main__":
    try:
        from termcolor import cprint
    except ImportError:
        def cprint(*args, **kwargs):
            print(*args)
    main()


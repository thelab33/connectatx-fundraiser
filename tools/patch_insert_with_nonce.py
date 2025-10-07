#!/usr/bin/env python3
"""
Auto-patch tool: replace .innerHTML = ... partial injection with
insertWithNonce(target, html) and inject the helper function into the
same <script> block if missing.

Usage:
  python tools/patch_insert_with_nonce.py <path> [<path> ...] [-n|--apply]

By default runs in dry-run mode and shows what would be changed.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

INJECTOR_FN = r'''
// nonce-aware injector (auto-inserted by patch_insert_with_nonce.py)
function insertWithNonce(target, html) {
  const tpl = document.createElement('template');
  tpl.innerHTML = String(html);

  const nonce = (window.__CSP_NONCE || '').trim() || null;

  // hoist external stylesheet links (dedupe by href)
  tpl.content.querySelectorAll('link[rel="stylesheet"][href]').forEach(link => {
    try {
      const href = link.getAttribute('href');
      if (!href) return;
      if (!document.querySelector('link[rel="stylesheet"][href="'+href+'"]')) {
        const l = document.createElement('link');
        l.rel = 'stylesheet';
        l.href = href;
        if (nonce) l.setAttribute('nonce', nonce);
        document.head.appendChild(l);
      }
    } catch (e) { console.warn('inject: hoist link failed', e); }
    link.remove();
  });

  // stamp nonce on inline <style>
  if (nonce) {
    tpl.content.querySelectorAll('style').forEach(s => {
      if (!s.getAttribute('nonce')) s.setAttribute('nonce', nonce);
    });
  }

  // re-create scripts so they execute (preserve attributes)
  tpl.content.querySelectorAll('script').forEach(old => {
    try {
      const s = document.createElement('script');
      for (let i = 0; i < old.attributes.length; i++) {
        const a = old.attributes[i];
        s.setAttribute(a.name, a.value);
      }
      if (nonce && !s.getAttribute('nonce')) s.setAttribute('nonce', nonce);
      s.text = old.text || old.textContent || '';
      old.replaceWith(s);
    } catch (e) {
      console.warn('inject: script replace failed', e);
    }
  });

  // replace children of target
  target.replaceChildren(tpl.content);
}
'''.strip() + "\n"

# pattern to find assignments like "BODY.innerHTML = await res.text();" or "CONTENT.innerHTML = html;"
ASSIGN_RE = re.compile(
    r'(?P<lhs>\b(?:BODY|CONTENT|PANEL|BODY_NODE|sheet_content|sheetContent|content|CONTENT)\s*\.\s*innerHTML)\s*=\s*(?P<rhs>(?:await\s+[^\;]+|[^\;]+))\s*;',
    flags=re.I
)

SCRIPT_OPEN_RE = re.compile(r'<script\b[^>]*>', flags=re.I)
SCRIPT_CLOSE_RE = re.compile(r'</script\s*>', flags=re.I)

def find_script_block_around(text: str, idx: int) -> Tuple[int,int,str]:
    """
    Given text and index into text, find the script block (start,end and tag text)
    that contains idx. Returns (open_idx, close_idx, opening_tag_text). If not found,
    returns (-1,-1,'').
    """
    # search backward for <script ...>
    m_open = None
    for m in SCRIPT_OPEN_RE.finditer(text):
        if m.start() > idx:
            break
        m_open = m
    if not m_open:
        return (-1, -1, '')
    # search forward from m_open.end() for </script>
    m_close = SCRIPT_CLOSE_RE.search(text, m_open.end())
    if not m_close:
        return (-1, -1, '')
    return (m_open.start(), m_close.end(), m_open.group(0))

def safe_backup(path: Path):
    bak = path.with_suffix(path.suffix + '.bak')
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
        print(f"  [backup] wrote {bak}")

def patch_file(path: Path, apply: bool=False) -> bool:
    txt = path.read_text(encoding='utf8')
    changed = False
    out = text = txt
    replacements = []
    # find all occurrences of the assignment pattern
    for m in ASSIGN_RE.finditer(txt):
        lhs = m.group('lhs').strip()
        rhs = m.group('rhs').strip()
        span = m.span()
        # compute target variable name (lhsObj)
        lhs_obj_match = re.match(r'([A-Za-z0-9_]+)\s*\.\s*innerHTML', lhs, flags=re.I)
        lhs_obj = lhs_obj_match.group(1) if lhs_obj_match else 'BODY'
        # build replacement code: preserve the rhs as-is
        replacement = f"const html = ({rhs});\ninsertWithNonce({lhs_obj}, html);"
        replacements.append((span, replacement))
    if not replacements:
        return False

    # we will do replacements from end to start to keep indices valid
    new_txt = txt
    for span, replacement in reversed(replacements):
        a,b = span
        new_txt = new_txt[:a] + replacement + new_txt[b:]
        changed = True

    # For every replacement, ensure we injected the helper into the enclosing <script> block.
    # We'll scan each replacement index (we used the original spans -> find new index by searching for replacement)
    for span, replacement in replacements:
        # Find the replacement in new_txt (first occurrence)
        idx = new_txt.find(replacement)
        if idx == -1:
            continue
        open_i, close_i, open_tag = find_script_block_around(new_txt, idx)
        if open_i == -1:
            # can't find script container; we'll inject helper before end of file (fallback)
            if 'function insertWithNonce(' not in new_txt:
                new_txt = new_txt + "\n<script>\n" + INJECTOR_FN + "</script>\n"
                print(f"  [info] injected helper at EOF fallback in {path}")
            continue
        # extract script content
        script_content = new_txt[open_i:close_i]
        if 'function insertWithNonce(' in script_content:
            # already present in this script block; nothing to do
            continue
        # inject helper immediately after opening <script ...> tag
        # find the opening tag end
        m_open_tag = SCRIPT_OPEN_RE.search(new_txt, open_i, close_i)
        if not m_open_tag:
            continue
        insert_pos = m_open_tag.end()
        # prepare injection: preserve indentation after tag by inserting newline + helper
        new_txt = new_txt[:insert_pos] + "\n" + INJECTOR_FN + new_txt[insert_pos:]
        print(f"  [inject] added helper inside <script> block in {path}")
        # update subsequent indices by re-searching (we will continue loop)
    # done
    if changed:
        print(f"Patching {path} (dry-run unless --apply):")
        # show a short snippet of before/after around first change
        first_replace_pos = replacements[0][0][0]
        start = max(0, first_replace_pos - 80)
        end = min(len(txt), replacements[0][0][1] + 80)
        snippet_before = txt[start:end]
        snippet_after = new_txt[start:end]
        print("  --- snippet before --------------------------------")
        print(snippet_before)
        print("  --- snippet after ---------------------------------")
        print(snippet_after)
        if apply:
            safe_backup(path)
            path.write_text(new_txt, encoding='utf8')
            print(f"  [applied] wrote {path}")
        else:
            print(f"  [dry-run] set --apply to modify the file: {path}")
    return changed

def gather_paths(inputs: List[str]) -> List[Path]:
    p = []
    for ip in inputs:
        ipath = Path(ip)
        if ipath.is_file():
            p.append(ipath)
        elif ipath.is_dir():
            # scan for .html files
            p.extend(sorted(ipath.rglob('*.html')))
        else:
            print(f"Warning: {ip} not found", file=sys.stderr)
    return p

def main(argv=None):
    parser = argparse.ArgumentParser(description="Patch templates to use insertWithNonce for HTML partial injection.")
    parser.add_argument('paths', nargs='+', help='Files or directories to scan (recurses directories for .html)')
    parser.add_argument('-a','--apply', action='store_true', help='Apply changes (default: dry-run)')
    args = parser.parse_args(argv)

    paths = gather_paths(args.paths)
    if not paths:
        print("No files found.")
        return 1

    any_changed = False
    for p in paths:
        try:
            changed = patch_file(p, apply=args.apply)
            any_changed = any_changed or changed
        except Exception as e:
            print(f"Error patching {p}: {e}", file=sys.stderr)

    if not any_changed:
        print("No changes required.")
    else:
        print("Done. Review .bak files for backups.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

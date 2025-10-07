#!/usr/bin/env python3
"""
fc_batch_scope.py
Auto-detect root class for each partial in app/templates/embed and run fc_extract_and_scope.py
Usage:
  python fc_batch_scope.py
"""
import os
import re
import shlex
import subprocess
from pathlib import Path

ROOT = Path('app/templates/embed')
CLI = Path('fc_extract_and_scope.py').resolve()

def detect_scope(file_path):
    txt = file_path.read_text(encoding='utf8')
    # look for first top-level div/article/section with a class attribute
    m = re.search(r'<(div|section|article)[^>]*\bclass\s*=\s*"([^"]+)"', txt, re.I)
    if m:
        classes = m.group(2).strip().split()
        # prefer classes that start with fc- or about- or tiers- etc.
        for c in classes:
            if c.startswith('fc-') or c.endswith('-sheet') or c.startswith('about') or c.startswith('tiers'):
                return '.' + c
        # otherwise return first class
        return '.' + classes[0]
    # fallback: choose filename-based scope
    fallback = '.' + file_path.stem.replace('_sheet','').replace('sheet','').replace('_','-')
    return fallback

def run_cli(infile, scope):
    out_css = f"static/css/{infile.stem}.scoped.css"
    out_html = str(infile.parent / f"{infile.stem}.scoped.html")
    cmd = [
        'python3', str(CLI),
        str(infile),
        '--out-css', out_css,
        '--out-html', out_html,
        '--scope', scope
    ]
    print('RUN:', ' '.join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)

def main():
    if not CLI.exists():
        print("ERROR: fc_extract_and_scope.py not found in project root. Place it next to this script.")
        return
    for f in sorted(ROOT.glob('*_sheet.html')):
        print("\nProcessing", f)
        scope = detect_scope(f)
        print("Detected scope:", scope)
        try:
            run_cli(f, scope)
        except subprocess.CalledProcessError as e:
            print("CLI returned non-zero:", e)
            continue

if __name__ == '__main__':
    main()


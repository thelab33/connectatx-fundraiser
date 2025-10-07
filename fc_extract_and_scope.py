#!/usr/bin/env python3
"""
fc_extract_and_scope.py

Extract inline <style> blocks from an HTML partial, prefix selectors with a scope
(e.g. ".fc-impact"), write a scoped CSS file, and emit an HTML partial with the
style blocks removed and a placeholder for the CSS link.

Usage:
  python fc_extract_and_scope.py templates/partials/impact_partial.html \
    --out-css static/css/fc-impact.scoped.css \
    --out-html templates/partials/impact_partial.scoped.html \
    --scope ".fc-impact" \
    --extract-scripts static/js/fc-impact.partial.js  # optional
"""
import re
import sys
import argparse
from pathlib import Path

def extract_blocks(html, tag):
    pattern = re.compile(rf'(<{tag}([^>]*)>)(.*?)(</{tag}>)', re.DOTALL | re.IGNORECASE)
    out = []
    for m in pattern.finditer(html):
        full = m.group(0)
        open_tag = m.group(1)
        attrs = m.group(2) or ''
        inner = m.group(3) or ''
        out.append((full, inner, attrs))
    return out

def remove_blocks(html, tag):
    pattern = re.compile(rf'<{tag}[^>]*>.*?</{tag}>', re.DOTALL | re.IGNORECASE)
    return pattern.sub('', html)

def find_unscoped_selectors(css_text, scope):
    selectors = []
    for sel in re.findall(r'([^{}]+)\{', css_text):
        s = sel.strip()
        if not s: continue
        if s.startswith('@'):
            continue
        for part in s.split(','):
            p = part.strip()
            selectors.append(p)
    unscoped = []
    for s in selectors:
        if scope in s:
            continue
        unscoped.append(s)
    return sorted(set(unscoped))

def prefix_css(css_text, scope):
    # naive prefixer: prefix comma-separated selectors that don't begin with '@' and don't already include scope
    def repl(m):
        sel = m.group(1)
        parts = [p.strip() for p in sel.split(',')]
        newparts = []
        for p in parts:
            if p == '' or p.startswith('@') or scope in p:
                newparts.append(p)
            else:
                p_fixed = p
                # if selector starts with html or :root, replace leading token to avoid global leakage
                if p_fixed.startswith('html'):
                    p_fixed = scope + p_fixed[len('html'):]
                elif p_fixed.startswith(':root'):
                    p_fixed = scope + p_fixed[len(':root'):]
                newparts.append(f"{scope} {p_fixed}")
        return ', '.join(newparts) + ' {'
    out = re.sub(r'([^{]+)\{', repl, css_text)
    return out

def main():
    parser = argparse.ArgumentParser(description="Extract inline styles, scope CSS to a widget root and produce external files.")
    parser.add_argument('input', help='Input partial HTML file')
    parser.add_argument('--out-css', default='fc-impact.scoped.css', help='Output CSS filename')
    parser.add_argument('--out-html', default='partial.scoped.html', help='Output HTML with styles removed (link placeholder inserted)')
    parser.add_argument('--scope', default='.fc-impact', help='CSS scope to prefix selectors with')
    parser.add_argument('--extract-scripts', help='Optional: write inline <script> contents to this JS file and replace scripts with a src placeholder')
    parser.add_argument('--keep-style-tags', action='store_true', help='Keep original <style> tags in output HTML (not recommended with CSP)')
    args = parser.parse_args()

    fin = Path(args.input)
    if not fin.exists():
        print("ERROR: input file not found:", fin)
        sys.exit(2)

    html = fin.read_text(encoding='utf8')

    # extract style blocks
    styles = extract_blocks(html, 'style')
    if not styles:
        print("No <style> blocks found in", fin)
    else:
        print(f"Found {len(styles)} <style> block(s). Concatenating...")

    css_joined = "\n\n".join(s[1] for s in styles).strip()

    if not css_joined:
        print("No CSS content extracted.")
    else:
        before_unscoped = find_unscoped_selectors(css_joined, args.scope)
        if before_unscoped:
            print(f"Selectors that do NOT mention '{args.scope}' (sample up to 10):")
            for s in before_unscoped[:10]:
                print("  ", s)
        else:
            print("Looks like CSS already contains scope token in selectors (or only at-rules).")

        scoped_css = prefix_css(css_joined, args.scope)

        after_unscoped = find_unscoped_selectors(scoped_css, args.scope)
        if after_unscoped:
            print(f"Warning: {len(after_unscoped)} selectors may still be unscoped (edge cases). Sample:")
            for s in after_unscoped[:10]:
                print("  ", s)
        else:
            print("All selectors appear scoped to", args.scope)

        Path(args.out_css).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_css).write_text(scoped_css, encoding='utf8')
        print("Wrote scoped CSS to", args.out_css)

    # optionally extract inline scripts
    js_out = ''
    if args.extract_scripts:
        scripts = extract_blocks(html, 'script')
        if not scripts:
            print("No inline <script> blocks found.")
        else:
            inline_scripts = []
            for full, inner, attrs in scripts:
                if re.search(r'\bsrc\s*=', attrs or '', flags=re.I):
                    continue
                inline_scripts.append(inner)
            js_out = "\n\n".join(inline_scripts).strip()
            if js_out:
                Path(args.extract_scripts).parent.mkdir(parents=True, exist_ok=True)
                Path(args.extract_scripts).write_text(js_out, encoding='utf8')
                print("Wrote extracted inline JS to", args.extract_scripts)
            else:
                print("No inline script content to extract (scripts may already be external).")

    # produce new HTML: remove style blocks (unless keep-style-tags) and optionally replace scripts with placeholder
    new_html = html
    if not args.keep_style_tags:
        new_html = remove_blocks(new_html, 'style')
        insert_token = f'<!-- INSERT_CSS_LINK: {args.out_css} -->\n'
        # insert after <body> if present, else at top
        if '<body' in new_html.lower():
            m = re.search(r'(<body[^>]*>)', new_html, re.I)
            if m:
                new_html = new_html[:m.end()] + '\n' + insert_token + new_html[m.end():]
            else:
                new_html = insert_token + new_html
        else:
            new_html = insert_token + new_html

    # replace inline scripts with placeholder if we extracted them
    if args.extract_scripts and js_out:
        def repl_script(m):
            attrs = m.group(2)
            if re.search(r'\bsrc\s*=', attrs or '', flags=re.I):
                return m.group(0)  # keep external script tags
            return f'<!-- INLINE_SCRIPT_EXTRACTED: {args.extract_scripts} -->\n<script src="{args.extract_scripts}"></script>'
        new_html = re.sub(r'(<script([^>]*)>)(.*?)(</script>)', repl_script, new_html, flags=re.DOTALL|re.I)

    Path(args.out_html).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_html).write_text(new_html, encoding='utf8')
    print("Wrote modified HTML (styles removed) to", args.out_html)

if __name__ == '__main__':
    main()


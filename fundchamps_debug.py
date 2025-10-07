import os
import re

# ---- CONFIG ----
SEARCH_EXTENSIONS = ['.html', '.htm', '.jinja', '.j2', '.css']
PROJECT_ROOT = os.getcwd()  # Change if not running from repo root

# ---- UTILS ----
def find_files(base_dir, exts):
    for root, _, files in os.walk(base_dir):
        for f in files:
            if any(f.lower().endswith(ext) for ext in exts):
                yield os.path.join(root, f)

def extract_classes(line):
    return re.findall(r'class=["\']([^"\']+)["\']', line)

def has_nonce(line):
    return re.search(r'nonce\s*=\s*["\']', line, re.IGNORECASE)

def looks_like_style(line):
    return '<style' in line or '</style>' in line

def looks_like_script(line):
    return '<script' in line or '</script>' in line

def looks_like_link(line):
    return '<link' in line and 'stylesheet' in line

def looks_like_csp(line):
    return 'csp' in line.lower() or 'nonce' in line.lower()

def is_modal_or_partial(filename):
    return any(x in filename.lower() for x in ['modal', 'partial', 'sheet'])

def suspicious_inline_css(line):
    return 'style="' in line or "style='" in line

# ---- MAIN SCRAPER ----
report = []
css_classes = set()
missing_nonces = []
inline_styles = []
file_summary = {}

print("\n\n--- FUNDCHAMPS LINTER: CSS & TEMPLATE DEBUG ---\n")

for filepath in find_files(PROJECT_ROOT, SEARCH_EXTENSIONS):
    lines = open(filepath, encoding='utf-8', errors='ignore').readlines()
    in_style_block = False
    in_script_block = False

    file_report = {'file': filepath, 'missing_nonce_lines': [], 'inline_style_lines': [], 'class_names': set()}

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Collect all class names
        for class_chunk in extract_classes(line):
            for c in class_chunk.split():
                file_report['class_names'].add(c)
                css_classes.add(c)

        # Inline <style> blocks without nonce
        if looks_like_style(line):
            if not has_nonce(line):
                file_report['missing_nonce_lines'].append((i+1, line.strip()))
                missing_nonces.append((filepath, i+1, line.strip()))

        # Inline <script> blocks without nonce
        if looks_like_script(line):
            if '<script' in line and not has_nonce(line):
                file_report['missing_nonce_lines'].append((i+1, line.strip()))
                missing_nonces.append((filepath, i+1, line.strip()))

        # Inline style attribute
        if suspicious_inline_css(line):
            file_report['inline_style_lines'].append((i+1, line.strip()))
            inline_styles.append((filepath, i+1, line.strip()))

        # Potential issues: CSP, duplicate styles, links, modals, partials
        # (Could expand with more checks as needed...)

    file_summary[filepath] = file_report

# ---- PRINT REPORT ----
for f, data in file_summary.items():
    print(f"\n>>> {f} <<<")
    if is_modal_or_partial(f):
        print("  (Modal/Partial detected)")

    if data['missing_nonce_lines']:
        print("  Lines missing nonce:")
        for ln, txt in data['missing_nonce_lines']:
            print(f"    Line {ln}: {txt}")

    if data['inline_style_lines']:
        print("  Inline style attributes (not recommended):")
        for ln, txt in data['inline_style_lines']:
            print(f"    Line {ln}: {txt}")

    if data['class_names']:
        preview = ", ".join(sorted(list(data['class_names']))[:10])
        print(f"  Unique classes found: {len(data['class_names'])} (e.g., {preview}{'...' if len(data['class_names'])>10 else ''})")

print("\n\n--- GLOBAL SUMMARY ---")
print(f"Total files checked: {len(file_summary)}")
print(f"Unique CSS classes found: {len(css_classes)}")
print(f"Inline styles flagged: {len(inline_styles)}")
print(f"Nonce issues flagged: {len(missing_nonces)}")

if missing_nonces:
    print("\n>> Potential CSP nonce issues found in these locations:")
    for f, ln, txt in missing_nonces:
        print(f"  {f} line {ln}: {txt}")

if inline_styles:
    print("\n>> Inline style attributes found (should move to CSS/tokens):")
    for f, ln, txt in inline_styles[:15]:
        print(f"  {f} line {ln}: {txt}")

print("\n--- Done! ---\n")

# === OPTIONAL: dump all unique classes for safelisting ===
# print("\nAll unique class names (for Tailwind safelist):\n", "\n".join(sorted(css_classes)))

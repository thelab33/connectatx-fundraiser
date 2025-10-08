import os
import re

TEMPLATES_ROOT = './templates'  # Change if your templates folder is elsewhere

# Regex patterns
OLD_MACRO_IMPORT = re.compile(
    r"{%\s*import\s+['\"][^'\"]+(_fmt\.html|macros\.html)['\"]\s+as\s+[\w]+\s*(with context)?\s*%}\s*\n?",
    re.IGNORECASE
)
NONCE_STYLE_TAG = re.compile(r"<style\s*\{\s*\{?\s*nonce_attr\(\)\s*\}?\s*\}\s*>", re.IGNORECASE)

NEW_MACRO_IMPORT = "{% import 'partials/macros.html' as fc with context %}\n"

def patch_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    # 1. Remove ALL old macro imports
    content, n_macro = OLD_MACRO_IMPORT.subn('', content)

    # 2. Insert the new macro import at the top (after any extends/includes/blocks)
    lines = content.split('\n')
    insert_idx = 0
    # Allow extends/imports/includes at the top, but insert before any macro/function/block definition
    for i, line in enumerate(lines):
        if line.strip().startswith('{%') and (
            'extends' in line or 'include' in line or 'block' in line or 'from' in line
        ):
            insert_idx = i + 1
        elif line.strip().startswith('{% macro') or line.strip().startswith('<!doctype'):
            break

    # Prevent duplicate insertion
    if NEW_MACRO_IMPORT.strip() not in content:
        lines.insert(insert_idx, NEW_MACRO_IMPORT.strip())

    # 3. Remove duplicate nonce style tags; only keep the first!
    found_first = False
    def style_nonce_replacer(match):
        nonlocal found_first
        if not found_first:
            found_first = True
            return match.group(0)
        else:
            return "<style>"  # Replace duplicates with simple <style>

    patched = '\n'.join(lines)
    patched = NONCE_STYLE_TAG.sub(style_nonce_replacer, patched)

    # Save only if changes
    if patched != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(patched)
        print(f"Patched: {path}")

def patch_all_templates(root):
    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith('.html') or file.endswith('.jinja'):
                patch_file(os.path.join(subdir, file))

if __name__ == '__main__':
    patch_all_templates(TEMPLATES_ROOT)
    print("\nAll macros imports and nonce style tags are now auto-patched! 🚀")


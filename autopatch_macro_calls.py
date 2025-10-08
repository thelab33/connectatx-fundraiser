import os
import re

TEMPLATE_DIR = './templates'  # change if your templates live elsewhere

# List any legacy macro aliases here
LEGACY_ALIASES = ['fmt', 'mc', 'macros', 'm']  # add others if needed
NEW_ALIAS = 'fc'

def patch_macros_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content

    for old in LEGACY_ALIASES:
        # Matches e.g. fmt.cta_btn( or mc.share_btn(
        content = re.sub(rf'\b{old}\.', f'{NEW_ALIAS}.', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Patched: {filepath}')

def walk_and_patch():
    for root, _, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html'):
                patch_macros_in_file(os.path.join(root, file))

if __name__ == '__main__':
    walk_and_patch()
    print("\nAll legacy macro calls now patched to use 'fc.'! 🚀")


# polish_audit.py
import glob
import re

files = glob.glob('**/*.html', recursive=True)
cta_regex = re.compile(r'class="[^"]*fcx-btn-accent[^"]*"')

for file in files:
    with open(file) as f:
        content = f.read()
    issues = []
    if 'max-width: 1100px' not in content:
        issues.append('Missing max-width: 1100px on sections')
    if not cta_regex.search(content):
        issues.append('Donate CTA missing .fcx-btn-accent')
    if 'floating-donate-cta' not in content:
        issues.append('No floating donate CTA')
    if issues:
        print(f"{file} needs polish: {', '.join(issues)}")
    else:
        print(f"{file}: Looks great!")


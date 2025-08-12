import os
import re
import shutil
from glob import glob

TEMPLATE_PATH = "app/templates"

def fix_class_attributes(line):
    # 1. Ignore Jinja2 lines
    if "{%" in line or "{{" in line:
        return line

    # 2. Regex for class="...." with bad stuff inside (e.g., aria-label=, accept=, fill=, viewBox=, etc.)
    class_attr_pattern = r'class="([^"]*)"'
    matches = list(re.finditer(class_attr_pattern, line))
    new_line = line

    for match in matches:
        classes = match.group(1)
        # Split by space, filter out anything that looks like key=val or includes =' or ="
        classnames = []
        extras = []
        for c in re.split(r"\s+", classes):
            if (
                re.match(r".*=(\"|').*", c)
                or re.match(r".*=(?![0-9])", c)
                or c.strip().endswith("=")
                or ":" in c  # Ignore arbitrary variants
            ):
                extras.append(c)
            else:
                classnames.append(c)
        # Optional: if all are junk, just blank out class
        if classnames:
            fixed = " ".join(classnames)
            # Replace only this match
            new_line = new_line.replace(match.group(0), f'class="{fixed}"')
        else:
            # Remove the class entirely
            new_line = new_line.replace(match.group(0), "")
        if extras:
            print(f"  [auto-fix] Removed from class: {extras}")

    # 3. Remove duplicated/malformed class attributes (e.g., class="=" or class="Thank you!" etc)
    new_line = re.sub(r'class="="?[\s,;:!?\.]*"?', '', new_line)

    return new_line

def backup_file(path):
    backup = path + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
        print(f"  [backup] Created backup: {backup}")

def process_file(filepath):
    changed = False
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        fixed = fix_class_attributes(line)
        if fixed != line:
            changed = True
        new_lines.append(fixed)

    if changed:
        backup_file(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"[fixed] {filepath}")

def main():
    print(f"🔍 Scanning {TEMPLATE_PATH} for template auto-fixes...")
    for root, dirs, files in os.walk(TEMPLATE_PATH):
        for fname in files:
            if fname.endswith(".html") or fname.endswith(".jinja") or fname.endswith(".j2"):
                fpath = os.path.join(root, fname)
                process_file(fpath)
    print("✅ Auto-fix complete. All changes are backed up with .bak extension.")

if __name__ == "__main__":
    main()


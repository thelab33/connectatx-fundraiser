import os
import re
from datetime import datetime
from termcolor import colored

# CONFIG
TEMPLATE_DIR = "app/templates/partials"
GENERIC_LABELS = [
    ('aria-label="Click me"', 'aria-label="REVIEW_ME"'),
    ('aria-label="Button"', 'aria-label="REVIEW_ME"'),
    ('aria-label="Input field"', 'aria-label="REVIEW_ME"'),
    ('alt="Image"', 'alt="REVIEW_ME"'),
    ('alt=""', 'alt="REVIEW_ME"'),
]
REPORT_FILE = f"label_upgrade_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

def upgrade_labels():
    report = ["# Accessibility Label Upgrade Report\n"]
    files_scanned = 0
    changes_made = 0

    for root, _, files in os.walk(TEMPLATE_DIR):
        for fname in files:
            if fname.endswith(".html"):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                original_content = content

                for old, new in GENERIC_LABELS:
                    if old in content:
                        occurrences = len(re.findall(re.escape(old), content))
                        content = content.replace(old, new)
                        if occurrences:
                            line_nums = [str(i+1) for i, line in enumerate(original_content.splitlines()) if old in line]
                            report.append(f"- **{fname}**: Replaced `{old}` with `{new}` on lines {', '.join(line_nums)}")
                            print(colored(f"[✔] {fname}: {old} → {new} ({occurrences} times)", "yellow"))
                            changes_made += occurrences
                if content != original_content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                files_scanned += 1

    report.append(f"\n**Total files scanned:** {files_scanned}")
    report.append(f"**Total changes made:** {changes_made}")
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(colored(f"\n🎉 All done! Review 'REVIEW_ME' in your templates and finalize labels.\nSee detailed changes in {REPORT_FILE}", "green"))

if __name__ == "__main__":
    upgrade_labels()


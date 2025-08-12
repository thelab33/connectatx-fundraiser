import os
import re
from pathlib import Path

LABEL_PATTERNS = [
    (r'aria-label="REVIEW_ME"', 'aria-label'),
    (r'alt="REVIEW_ME"', 'alt')
]

def get_context(lines, idx, window=2):
    """Get a few lines of context for CLI display."""
    start = max(0, idx-window)
    end = min(len(lines), idx+window+1)
    return ''.join(lines[start:end])

def main():
    root = Path('app/templates/partials')
    files = list(root.glob("*.html"))
    total_changes = 0
    changes = []
    print("\n🔎 Scanning templates for placeholders...")

    for file in files:
        with file.open('r', encoding='utf-8') as f:
            lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            for pattern, attr in LABEL_PATTERNS:
                if pattern in line:
                    print(f"\n📄 {file.name} | line {i+1}")
                    print(get_context(lines, i))
                    user_input = input(f"  → Enter replacement for `{attr}` (or leave blank to skip): ").strip()
                    if user_input:
                        repl = f'{attr}="{user_input}"'
                        lines[i] = re.sub(f'{attr}="REVIEW_ME"', repl, line)
                        print(f"    ✔️ Replaced with: {repl}")
                        changes.append(f"{file.name}: line {i+1} → {repl}")
                        total_changes += 1
                        updated = True
                    else:
                        print("    ⏭️  Skipped.")

        if updated:
            with file.open('w', encoding='utf-8') as f:
                f.writelines(lines)

    # Write report
    if changes:
        with open('label_wizard_report.md', 'w') as f:
            f.write("# Accessibility Label Wizard Report\n\n")
            f.write(f"**Total changes made:** {total_changes}\n\n")
            for c in changes:
                f.write(f"- {c}\n")
        print(f"\n🎉 All done! {total_changes} label(s) updated.")
        print("📄 See `label_wizard_report.md` for a summary.\n")
    else:
        print("\n✅ No placeholders found! You're all set.\n")

if __name__ == "__main__":
    main()


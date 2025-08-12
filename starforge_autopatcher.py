import os
import re
from pathlib import Path
from datetime import datetime

ROOT = Path('app/templates')
SUMMARY = []
REVIEW_TAG = "REVIEW_ME"

# Patterns to fix/flag
BAD_LABELS = [
    r'aria-label="(Click me|Icon|REVIEW_ME)"',
    r'alt="(Image|REVIEW_ME|)"',
]
MALFORMED_CLASS = [
    (r'class=" +', 'class="'),
    (r'" +', '"'),
]
DUPLICATE_ATTR = [
    r'(\bid="[^"]+"\s+.*\bid="[^"]+")',
    r'(\bclass="[^"]+"\s+.*\bclass="[^"]+")',
]

def scan_and_patch():
    patched = 0
    for html_file in ROOT.rglob("*.html"):
        text = html_file.read_text(encoding='utf-8')
        orig = text

        # 1. Mark placeholder aria/alt for review
        for pat in BAD_LABELS:
            text, n = re.subn(pat, f'aria-label="{REVIEW_TAG}"', text)
            if n:
                SUMMARY.append(f"[aria/alt label] {html_file}: {n} instance(s) patched to '{REVIEW_TAG}'")
                patched += n

        # 2. Clean malformed classes and common bad strings
        for pat, rep in MALFORMED_CLASS:
            text, n = re.subn(pat, rep, text)
            if n:
                SUMMARY.append(f"[class fix] {html_file}: {n} malformed class strings fixed")
                patched += n

        # 3. Find duplicates (mark in summary, don't patch automatically)
        for pat in DUPLICATE_ATTR:
            for m in re.finditer(pat, text):
                SUMMARY.append(f"[DUPLICATE ATTR] {html_file}: Line {text.count('\\n', 0, m.start())+1}: {m.group(0)[:60]}...")

        # 4. Custom patch: Bad onclick/JS
        text, n = re.subn(r'onclick="this.closestdialog.close', 'onclick="this.closest(\'dialog\').close()', text)
        if n:
            SUMMARY.append(f"[onclick fix] {html_file}: {n} bad JS attribute(s) fixed")
            patched += n

        # 5. Write back if changed
        if text != orig:
            html_file.write_text(text, encoding='utf-8')

    return patched

def write_report():
    report_path = f"autopatch_report_{datetime.now():%Y-%m-%d_%H%M%S}.md"
    with open(report_path, "w") as f:
        f.write(f"# Starforge Autopatch Report — {datetime.now()}\n\n")
        f.write(f"**Total changes made:** {sum('patched' in s for s in SUMMARY)}\n\n")
        for s in SUMMARY:
            f.write("- " + s + "\n")
    print(f"✅ Autopatch complete. See {report_path}")

if __name__ == "__main__":
    print("🔍 Scanning for issues...")
    n = scan_and_patch()
    write_report()
    print(f"\n🎉 {n} changes auto-patched.\nReview the report for flagged lines needing review/QA.")



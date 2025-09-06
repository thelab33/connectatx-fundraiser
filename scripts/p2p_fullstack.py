#!/usr/bin/env python3
import re, sys, subprocess, pathlib

PARTIALS = {
    "hero": "app/templates/partials/hero_and_fundraiser.html",
    "header": "app/templates/partials/header_and_announcement.html",
    "tiers": "app/templates/partials/tiers.html",
    "impact": "app/templates/partials/impact_lockers_premium.html",
    "about": "app/templates/partials/about_section.html",
    "footer": "app/templates/partials/footer.html",
    "base": "app/templates/base.html",
}

def patch_file(path, where):
    text = pathlib.Path(path).read_text(encoding="utf-8")

    # Example: add data-p2p-propagate to Donate/Sponsor links
    text = re.sub(
        r'(<a[^>]+(?:donate|sponsor)[^>]*)(?<!data-p2p-propagate)',
        r"\1 data-p2p-propagate='1' data-analytics='cta_click' "
        f"data-analytics-meta='{{{{ {{ 'where': '{where}' }} | tojson }}}}'",
        text,
        flags=re.IGNORECASE,
    )

    pathlib.Path(path).write_text(text, encoding="utf-8")
    print(f"✔ Patched {path}")

def check_nonce(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if "{{ nonce_attr() }}" not in text:
        print(f"❌ Missing nonce_attr in {path}")
        sys.exit(1)

def run_lighthouse():
    try:
        subprocess.run(
            ["lhci", "autorun", "--collect.url=http://localhost:5000"],
            check=True,
        )
    except FileNotFoundError:
        print("⚠️ Lighthouse CI not installed. Run: npm install -g @lhci/cli")

def main():
    for where, path in PARTIALS.items():
        if "base" in where:  # simpler meta injection example
            continue
        patch_file(path, where)
        check_nonce(path)

    run_lighthouse()

if __name__ == "__main__":
    main()


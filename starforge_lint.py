#!/usr/bin/env python3
import re, os, sys
from pathlib import Path
from bs4 import BeautifulSoup
from rich.console import Console
import click

# Tailwind classes you use most (expand as needed or auto-load from your config)
COMMON_TAILWIND = set([
    'bg-yellow-400', 'rounded-full', 'shadow-2xl', 'text-white', 'flex',
    # ...add more as your project grows
])

console = Console()

def find_broken_class_attrs(content):
    # Catches: class=..., class=", class="missing, class="no-end, etc
    pattern = r'class\s*=\s*["\']?([^"\'>\s][^"\'>]*)(?=[\s>])'
    # Also: class="something no-close
    broken = re.findall(pattern, content)
    return broken

def check_tailwind_classes(classes):
    return [cls for cls in classes.split() if cls and cls not in COMMON_TAILWIND and not cls.startswith('bg-') and not cls.startswith('text-') and not cls.startswith('ring-') and not cls.startswith('shadow')]

def lint_file(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Find broken classes
    broken = []
    for line_no, line in enumerate(content.splitlines(), 1):
        if 'class=' in line:
            if not re.search(r'class="[^"]*"', line) and not re.search(r"class='[^']*'", line):
                broken.append((line_no, line.strip()))
            else:
                # Flag unknown tailwind classes (if desired)
                for match in re.findall(r'class="([^"]+)"', line):
                    unknown = check_tailwind_classes(match)
                    if unknown:
                        broken.append((line_no, f"Unknown Tailwind: {', '.join(unknown)} -> {line.strip()}"))
    return broken

@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    root = Path(path)
    total = 0
    for p in root.rglob("*.html"):
        issues = lint_file(p)
        if issues:
            console.rule(f"[bold yellow]{p}")
            for ln, snippet in issues:
                console.print(f"[red bold]Line {ln}:[/red bold] [white]{snippet}[/white]")
            total += len(issues)
    if total == 0:
        console.print("[bold green]No issues found![/bold green] 🚀")
    else:
        console.print(f"[bold red]{total} issues found. Fix recommended![/bold red]")

if __name__ == '__main__':
    main()


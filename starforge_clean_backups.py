# starforge_clean_backups.py
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
moved = 0
for f in root.rglob("*.bak*"):
    target = f.parent / "_backups"
    target.mkdir(exist_ok=True)
    shutil.move(str(f), target / f.name)
    moved += 1

print(f"✅ Moved {moved} backup files into _backups/")


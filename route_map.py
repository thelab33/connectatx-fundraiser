#!/usr/bin/env python3
"""
FundChamps Route Map — static scan (best-effort)
Usage: python route_map.py [root_dir]
Scans .py files for Blueprint registration and route decorators.
"""
import sys, re
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
pat_bp = re.compile(r"Blueprint\(\s*['\"]([A-Za-z0-9_\-]+)['\"]\s*,\s*__name__")
pat_route = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)\.(?:route|get|post|put|delete)\(\s*['\"]([^'\"]+)['\"]")

bps = {}
routes = []
for p in root.rglob('*.py'):
    if '.git' in p.parts: continue
    try:
        s = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    for m in pat_bp.finditer(s):
        bps.setdefault(m.group(1), []).append(str(p))
    for m in pat_route.finditer(s):
        routes.append((m.group(1), m.group(2), str(p)))

print('== Blueprints (by name) ==')
for name, files in sorted(bps.items()):
    print(f"{name}: {len(files)} file(s)")
    for f in files:
        print(f"  - {f}")

print('\n== Routes (blueprint.var / path) ==')
for bpvar, path, file in sorted(routes):
    print(f"{bpvar:15s} -> {path:30s} ({file})")

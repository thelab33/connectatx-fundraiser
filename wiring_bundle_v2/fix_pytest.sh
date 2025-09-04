#!/usr/bin/env bash
set -euo pipefail

echo "👉 Creating pytest.ini pinned to tests/ and ignoring fundchamps*/"
cat > pytest.ini <<'INI'
[pytest]
testpaths = tests
python_files = test_*.py
norecursedirs = .git .hg .svn .venv venv env build dist node_modules fundchamps fundchamps* */fundchamps
addopts = -q
INI

echo "👉 Removing duplicate root-level tests if present"
rm -f ./test_wiring.py || true

echo "👉 Clearing caches"
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
find . -name "*.pyc" -delete

echo "Done. Run: BASE_URL=http://localhost:5000 pytest -q"

#!/usr/bin/env bash
set -euo pipefail

ROOT="app/templates"
URL="${URL:-http://127.0.0.1:5000/}"  # change if your dev server runs elsewhere
RG="$(command -v rg || true)"
GREP="grep -RIn"
if [[ -n "$RG" ]]; then GREP="$RG -nH"; fi

echo "==[ HEADER AUDIT : $(date -Is) ]==============================="
echo "Repo: $(pwd)"
echo "Templates root: $ROOT"
echo "Curl target: $URL"
echo

# 0) Sanity: show any alternative base files that could shadow each other
echo ">> Base candidates (shadow risk)"
find "$ROOT" -maxdepth 3 -type f -iregex '.*/base[^/]*\.html(\.jinja)?$' -print | sort
echo

# 1) Which templates extend base.html (could override blocks)
echo ">> Templates that extend base.html"
$GREP -- '\{%\s*extends\s*"base\.html"\s*%}' "$ROOT" || true
echo

# 2) Where is the header block defined/overridden?
echo ">> Files that define/override '{% block header %}'"
$GREP -- '\{%\s*block\s+header(\s+%|%})' "$ROOT" | sed 's/^/  /' || true
echo

# 3) Includes graph: all partials included anywhere (unique list + who includes them)
echo ">> Unique partial includes (path)"
$GREP -- '\{%\s*include\s*"partials/[^"]+' "$ROOT" \
| sed -E 's/.*include *"([^"]+)".*/\1/' | sort -u
echo

echo ">> Where each header partial is included"
for p in 'partials/header_and_announcement.html' 'partials/_header_sv_elite.html.jinja' ; do
  echo "  - $p"
  $GREP -- "include\\s+\"$p\"" "$ROOT" || echo "    (not referenced)"
done
echo

# 4) Do we have more than one #site-header in templates?
echo ">> Files that contain id=\"site-header\" (multiple creates duplicate headers)"
$GREP -- 'id="site-header"' "$ROOT" | sed 's/^/  /' || true
echo

# 5) Do we ship more than one Skip-to-content anchor from templates?
echo ">> Files that contain 'Skip to content' anchors"
$GREP -- '<a[^>]+href="#main"[^>]*>[^<]*Skip to content' "$ROOT" | sed 's/^/  /' || true
echo

# 6) Look for the corrupted regex-like line that kept appearing
echo ">> Corruption check for stuck regex blob (Skip to contents)"
$GREP -- 'main\"[^>]*>s*Skip to contents' "$ROOT" || echo "  none"
echo

# 7) Scan for any include AFTER </html> (junk appenders)
echo ">> Includes after </html> (bad: indicates appended junk)"
while IFS= read -r -d '' f; do
  if awk '/<\/html>/{found=1} found && /{% *include /{print FILENAME":"NR":"$0}' "$f"; then :; fi
done < <(find "$ROOT" -type f -print0)
echo

# 8) Ensure base.html uses ONLY your header partial in its header block
echo ">> Base header block content (base.html only)"
awk '
  /{%\s*block\s+header\s*%}/ {inb=1; print "---- BEGIN header block ("FILENAME") ----"}
  inb {print}
  /{%\s*endblock\s*%}/ && inb {inb=0; print "---- END header block ("FILENAME") ----\n"}
' "$ROOT/base.html" || true
echo

# 9) Verify the header partial actually exists on disk (name must match includes)
echo ">> Existence check: header partial files"
for p in \
  "$ROOT/partials/header_and_announcement.html" \
  "$ROOT/partials/_header_sv_elite.html.jinja" \
  "$ROOT/partials/_elite_header.html" \
; do
  if [[ -f "$p" ]]; then echo "  ✔ $p"; else echo "  ✖ $p (missing)"; fi
done
echo

# 10) Check rendered HTML (live) to count headers & skip links
#     Requires server running. This helps confirm "real" duplicates.
echo ">> LIVE curl check (counts on $URL)"
if command -v curl &>/dev/null; then
  html="$(curl -fsSL "$URL" || true)"
  if [[ -n "${html}" ]]; then
    echo "  #site-header occurrences: $(grep -o 'id="site-header"' <<<"$html" | wc -l | tr -d ' ')"
    echo "  Skip-to-content anchors : $(grep -oE '<a[^>]+href="#main"[^>]*>[^<]*Skip to content' <<<"$html" | wc -l | tr -d ' ')"
    echo "  header_and_announcement in output?: $(grep -o 'header_and_announcement' <<<"$html" | wc -l | tr -d ' ')"
    echo "  elite header marker (if any)       : $(grep -o '_header_sv_elite' <<<"$html" | wc -l | tr -d ' ')"
    echo
    echo "  Top of <body> snippet:"
    awk 'BEGIN{p=0} /<body/{p=1} p && NR<=120{print} /<main[^>]*id="main"/{exit}' <<<"$html"
  else
    echo "  (curl failed or server not running)"
  fi
else
  echo "  curl not found; skipping live check"
fi
echo

# 11) BOM / hidden bytes at file heads (rare, but can break Jinja parsing)
echo ">> BOM check (should be empty output)"
while IFS= read -r -d '' f; do
  head -c 3 "$f" | hexdump -Cv | awk -v F="$f" 'index($0,"ef bb bf"){print "  BOM in: "F}'
done < <(find "$ROOT" -type f -name '*.html*' -print0)
echo

# 12) CSP nonce macro duplication (can cause inline <a> or script duplication by auto-includes)
echo ">> Files defining nonce_attr macro"
$GREP -- '{% *macro +nonce_attr' "$ROOT" | sed 's/^/  /' || true
echo

# 13) Body/main structural sanity (multiple <body>, stray '</html>' in the middle, etc.)
echo ">> Structural sanity (counts should be 1 each in base.html)"
for tag in body html main; do
  c=$(grep -o "<$tag\\b" "$ROOT/base.html" | wc -l | tr -d ' ')
  echo "  <$tag> in base.html: $c"
done
echo

echo "==[ END AUDIT ]=========================================="


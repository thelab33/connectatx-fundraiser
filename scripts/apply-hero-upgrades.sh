#!/usr/bin/env bash
# ==========================================================
# FundChamps — Hero Partial Elite Upgrades (SV Edition)
# Jinja-safe, idempotent, variable-driven.
# Usage: ./scripts/apply-hero-upgrades.sh [path-to-hero.html]
# ==========================================================

set -euo pipefail

HERO_FILE="${1:-app/templates/partials/hero_and_fundraiser.html}"

log() { printf "\033[1;33m[fc-upgrade]\033[0m %s\n" "$*"; }
ok() { printf "\033[1;32m[OK]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;31m[WARN]\033[0m %s\n" "$*"; }
die() { printf "\033[1;31m[ERROR]\033[0m %s\n" "$*" >&2; exit 1; }

command -v perl >/dev/null || die "perl is required."
command -v grep >/dev/null || die "grep is required."
[[ -f "$HERO_FILE" ]] || die "File not found: $HERO_FILE"

TS="$(date +%F-%H%M%S)"
BACKUP="${HERO_FILE}.${TS}.bak"
cp "$HERO_FILE" "$BACKUP"
log "Backup created: $BACKUP"

patch_perl() {
  local description="$1" search="$2" replacement="$3"
  log "$description"
  perl -0777 -i -pe "s|$search|$replacement|s" "$HERO_FILE" || die "Patch failed: $description"
  ok "$description applied"
}

# 1) CSP nonce
if grep -q '<script' "$HERO_FILE" && ! grep -q 'nonce="{{ csp_nonce() }}"' "$HERO_FILE"; then
  patch_perl "Adding CSP nonce to <script> tags" \
    '<script(?![^>]*\bnonce=)' \
    '<script nonce="{{ csp_nonce() }}"'
else
  warn "CSP nonce already present or no <script> blocks"
fi

# 2) Progressbar semantics
if grep -q 'class="meter-wrap"' "$HERO_FILE" && ! grep -q 'role="progressbar"' "$HERO_FILE"; then
  pb_repl='<div class="meter-wrap"\1 role="progressbar" aria-label="Fundraising progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{{ pct\|int }}">'
  patch_perl "Adding progressbar role/aria" \
    '<div class="meter-wrap"(?![^>]*\brole=)([^>]*)>' \
    "$pb_repl"
else
  warn "Progressbar semantics already present"
fi

# 3) SR-only live region
if ! grep -q 'id="fc-sr"' "$HERO_FILE"; then
  sr_repl='</section>\n          <p id="fc-sr" class="sr-only" aria-live="polite" aria-atomic="true">Raised {{ (fundsRaised\|int) }} of {{ (fundraisingGoal\|int) }} ({{ pct }}%).</p>'
  patch_perl "Inserting SR-only aria-live region" \
    '</section>' \
    "$sr_repl"
else
  warn "SR live region already present"
fi

# 4) Link meter to SR live region
if grep -q 'role="progressbar"' "$HERO_FILE" && ! grep -q 'aria-describedby="fc-sr"' "$HERO_FILE"; then
  pb_desc_repl='\1 aria-describedby="fc-sr"\2'
  patch_perl "Linking meter to SR live region" \
    '(<div class="meter-wrap"[^>]*\brole="progressbar"[^>]*)(>)' \
    "$pb_desc_repl"
else
  warn "aria-describedby already set"
fi

# 5) prefers-reduced-motion CSS
if ! grep -q 'prefers-reduced-motion' "$HERO_FILE"; then
  css_repl='\1\n@media (prefers-reduced-motion: reduce){#fc-hero .meter-bar{transition:none}#site-header.is-shrunk,#fc-hero .cta{transition:none}}'
  patch_perl "Adding reduced-motion CSS" \
    '(<style>)' \
    "$css_repl"
else
  warn "Reduced-motion CSS already present"
fi

# 6) JS: SR narration
if ! grep -q 'sr.textContent' "$HERO_FILE"; then
  js_sr_repl='\1\n        const sr = document.querySelector("#fc-sr"); if (sr) sr.textContent = `Raised \${fmt(r)} of \${fmt(g)} (\${clampedPct.toFixed(1)}%).`;'
  patch_perl "Adding JS narration for SR live region" \
    '(percentEl\.textContent\s*=\s*clampedPct\.toFixed\(1\) \+ \'%\';\s*animateMeter\(clampedPct\);)' \
    "$js_sr_repl"
else
  warn "SR narration code already present"
fi

# 7) Idle-init polling
if grep -q 'setInterval(fetchStats, config.pollInterval);' "$HERO_FILE" && ! grep -q 'requestIdleCallback' "$HERO_FILE"; then
  poll_repl='(window.requestIdleCallback||setTimeout)(()=>{ setInterval(fetchStats, config.pollInterval); }, 250);'
  patch_perl "Wrapping polling in requestIdleCallback" \
    'setInterval\(fetchStats,\s*config\.pollInterval\);' \
    "$poll_repl"
else
  warn "Polling already idle-initialized"
fi

# 8) Keyboard shortcut + visibility refresh
if ! grep -q 'Quick Donate' "$HERO_FILE" && ! grep -q 'visibilitychange' "$HERO_FILE"; then
  kb_repl='init();\n      document.addEventListener("keydown",function(e){var t=(e.target||{}).tagName;if(t==="INPUT"||t==="TEXTAREA"||t==="SELECT")return;if(e.key==="d"||e.key==="D"){e.preventDefault();openDonationModal();}});\n      document.addEventListener("visibilitychange",function(){ if(!document.hidden) fetchStats(); });\n'
  patch_perl "Adding keyboard shortcut (D) & focus refresh" \
    '\binit\(\);\s*\n' \
    "$kb_repl"
else
  warn "Keyboard & visibility handlers already present"
fi

# 9) JSON-LD SEO
if ! grep -q 'application/ld+json' "$HERO_FILE"; then
  jsonld_repl='<script type="application/ld+json" nonce="{{ csp_nonce() }}">{"@context":"https://schema.org","@type":"SportsOrganization","name":"{{ teamName }}","logo":"{{ logoSrc }}"}</script>\n\1'
  patch_perl "Injecting JSON-LD SportsOrganization" \
    '(</section>\s*)\z' \
    "$jsonld_repl"
else
  warn "JSON-LD already present"
fi

# 10) Sidebar content-visibility
if grep -q '<aside class="lg:col-span-1"' "$HERO_FILE" && ! grep -q 'content-visibility:auto' "$HERO_FILE"; then
  aside_repl='<aside class="lg:col-span-1" style="content-visibility:auto;contain-intrinsic-size:1px 320px"'
  patch_perl "Adding content-visibility:auto to sidebar" \
    '<aside class="lg:col-span-1"' \
    "$aside_repl"
else
  warn "Sidebar content-visibility already set"
fi

log "All patches processed ✔"
log "Verify: git diff -- $HERO_FILE"
log "Restore: cp '$BACKUP' '$HERO_FILE'"


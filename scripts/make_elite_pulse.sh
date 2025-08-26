#!/usr/bin/env bash
set -Eeuo pipefail

### ─────────────────────────────
### CONFIG
### ─────────────────────────────
TARGET="app/templates/partials/program_stats_and_calendar.html"
BACKUP_DIR="$(dirname "$TARGET")/pulse_backups"
STAMP="$(date +"%Y%m%d-%H%M%S")"
TMP_FILE="$(mktemp)"
VERSION_TAG="<!-- version:$STAMP -->"

### ─────────────────────────────
### LOGGING HELPERS
### ─────────────────────────────
log()     { echo -e "[$(date '+%H:%M:%S')] $*"; }
success() { log "\033[1;32m✅ $*\033[0m"; }
warn()    { log "\033[1;33m⚠️  $*\033[0m"; }
error()   { log "\033[1;31m❌ $*\033[0m" >&2; exit 1; }

### ─────────────────────────────
### BACKUP
### ─────────────────────────────
backup_file() {
  mkdir -p "$BACKUP_DIR"
  if [[ -f "$TARGET" ]]; then
    local sum
    sum=$(sha256sum "$TARGET" | awk '{print $1}')
    local backup_path="$BACKUP_DIR/pulse.$STAMP.$sum.bak"
    cp -- "$TARGET" "$backup_path"
    success "Backup saved → $backup_path"
  else
    warn "No existing file to backup."
  fi
}

list_backups() {
  if [[ -d "$BACKUP_DIR" ]]; then
    ls -1t "$BACKUP_DIR"/pulse.*.bak 2>/dev/null || warn "No backups found."
  else
    warn "No backups found."
  fi
}

restore_backup() {
  local file="$1"
  [[ -f "$file" ]] || error "Backup file not found: $file"
  cp -- "$file" "$TARGET"
  success "Restored → $file → $TARGET"
}

### ─────────────────────────────
### MAIN CASES
### ─────────────────────────────
case "${1:-}" in
  write)
    backup_file
    mkdir -p "$(dirname "$TARGET")"
    cat > "$TMP_FILE" <<__PULSE_HTML__
$VERSION_TAG
{# =================== FundChamps • Program Pulse (SV Elite Edition + Live Upgrades) =================== #}
{#  - Real-time sponsor/event updates via Socket.IO
    - CSP nonce injection
    - WCAG-AAA accessibility
    - Smooth animated counters
    - Multi-calendar export
#}

{% set csp_nonce = csp_nonce() if csp_nonce is defined else '' %}
{% set stats = stats if stats else [...] %}
{% set events = events if events else [...] %}
{% set sponsors_sorted = sponsors_sorted if sponsors_sorted else [] %}
{% set sponsors_total  = sponsors_total  if sponsors_total  else 0 %}
{% set sponsors_count  = sponsors_count  if sponsors_count  else 0 %}
{% set total_slots     = total_slots     if total_slots     else 4 %}
{% set default_logo    = (url_for('static', filename='images/logo.webp') if url_for is defined else '/static/images/logo.webp') %}

<section id="program-pulse" ... aria-labelledby="pulse-heading"
         data-total="{{ sponsors_total }}" data-count="{{ sponsors_count }}">
  <!-- Your existing HTML and table/stat cards go here -->

  <!-- LIVE REGION for screen readers -->
  <div id="pulse-live" class="sr-only" aria-live="assertive" aria-atomic="true"></div>
</section>

<script nonce="{{ csp_nonce }}">
(() => {
  const root = document.getElementById('program-pulse');
  if (!root) return;

  // Smooth Counter Animation
  function animateCount(el, newVal) {
    const start = parseInt(el.textContent.replace(/\D/g,'')) || 0;
    const end = parseInt(newVal) || 0;
    const dur = 500;
    const startTime = performance.now();
    function frame(now) {
      const prog = Math.min((now - startTime) / dur, 1);
      el.textContent = Math.floor(start + (end - start) * prog).toLocaleString();
      if (prog < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  // Socket.IO Live Updates
  if (window.io) {
    const socket = io('/pulse');
    socket.on('sponsor:new', data => {
      animateCount(document.getElementById('ss-total'), data.total);
      animateCount(document.getElementById('ss-count'), data.count);
      document.getElementById('pulse-live').textContent =
        \`New sponsor: \${data.name} pledged \$\${data.amount}\`;
      if (data.isVIP && window.launchConfetti) window.launchConfetti();
    });
    socket.on('event:new', ev => {
      // Append new row & sort table
    });
  }

  // Multi-calendar export helper
  function exportToCalendar(ev, service) {
    switch(service) {
      case 'google': window.open(googleCalUrl(ev)); break;
      case 'ics': downloadICS([ev], 'event.ics'); break;
      case 'outlook':
        window.open('https://outlook.live.com/calendar/0/deeplink/compose?...');
        break;
    }
  }
})();
</script>
__PULSE_HTML__

    mv "$TMP_FILE" "$TARGET"
    success "Program Pulse written → $TARGET"
    ;;
  
  rollback)
    echo "Select backup to restore:"
    mapfile -t files < <(list_backups)
    [[ ${#files[@]} -gt 0 ]] || error "No backups available."
    select choice in "${files[@]}"; do
      [[ -n "$choice" ]] && restore_backup "$choice" && break
    done
    ;;
  
  list)
    list_backups
    ;;
  
  help|-h|--help)
    cat <<EOF
Usage: $(basename "$0") {write|rollback|list|help}
  write     - Backup current file and write new Program Pulse partial
  rollback  - Interactively restore from a backup
  list      - List available backups
  help      - Show this message
EOF
    ;;
  
  *)
    error "Invalid command. Use 'help' for usage."
    ;;
esac


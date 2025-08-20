#!/usr/bin/env bash
set -euo pipefail

echo "╭──────────────────────────────────────────────╮"
echo "│  🛠️  Starforge Partial Super-Patcher (SV)    │"
echo "╰──────────────────────────────────────────────╯"

if [ $# -lt 1 ]; then
  echo "Usage: $0 [--restore <partial>] <partial> [partial ...]"
  echo "  e.g. $0 hero about header footer"
  echo "       $0 --restore hero"
  exit 1
fi

TS=$(date +%Y%m%d-%H%M%S)

# --- Restore mode ---
if [ "$1" = "--restore" ]; then
  if [ $# -lt 2 ]; then
    echo "❌ Must specify which partial to restore"
    exit 1
  fi
  PART="$2"
  case "$PART" in
    hero)   FILE="app/templates/partials/hero_and_fundraiser.html" ;;
    about)  FILE="app/templates/partials/about_section.html" ;;
    header) FILE="app/templates/partials/header_and_announcement.html" ;;
    footer) FILE="app/templates/partials/footer.html" ;;
    *) echo "❌ Unknown partial: $PART"; exit 1 ;;
  esac

  LAST_BACKUP=$(ls -t "$FILE".bak.* 2>/dev/null | head -n1 || true)
  if [ -z "$LAST_BACKUP" ]; then
    echo "❌ No backup found for $PART ($FILE)"
    exit 1
  fi

  cp "$LAST_BACKUP" "$FILE"
  echo "↩️  Restored: $PART → $FILE (from $LAST_BACKUP)"
  exit 0
fi

# --- Normal patching loop ---
for name in "$@"; do
  case "$name" in
    hero)
      FILE="app/templates/partials/hero_and_fundraiser.html"
      BLOCK="{# --- Full Hero Block (fundraising math + deadline) --- #}
{% set NONCE = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}
{% set team_name = (team.team_name if team and team.team_name else 'Connect ATX Elite') %}
{% set theme_hex = (team.theme_color if team and team.theme_color else '#f59e0b') %}
{% set funds_raised = (funds_raised if funds_raised is defined else 0) | float %}
{% set fundraising_goal = (fundraising_goal if fundraising_goal is defined else 10000) | float %}
{% set fundraiser_deadline = (fundraiser_deadline if fundraiser_deadline is defined else none) %}
{% set pct = ((funds_raised / fundraising_goal) * 100) | round(1) if fundraising_goal else 0 %}
<section id='fc-hero' class='relative overflow-clip min-h-[82vh] flex items-center justify-center text-center text-white'>
  <img src='{{ hero_bg|default(url_for(\"static\", filename=\"images/hero.webp\")) }}' alt='' class='absolute inset-0 w-full h-full object-cover opacity-60'>
  <div class='relative z-10 px-6'>
    <h1 class='text-4xl md:text-6xl font-extrabold drop-shadow'>{{ team_name }} — Fundraiser</h1>
    <p class='mt-4 text-lg md:text-xl opacity-90'>Together we’ve raised <strong>\${{ \"{:,.0f}\".format(funds_raised) }}</strong> of our <strong>\${{ \"{:,.0f}\".format(fundraising_goal) }}</strong> goal!</p>
    <div class='mt-6 w-full max-w-lg mx-auto bg-white/20 rounded-full overflow-hidden'>
      <div class='h-4 bg-[{{ theme_hex }}]' style='width: {{ pct }}%;'></div>
    </div>
    {% if fundraiser_deadline %}
    <p class='mt-2 text-sm opacity-80'>Deadline: {{ fundraiser_deadline.strftime('%B %d, %Y') }}</p>
    {% endif %}
  </div>
</section>"
      ;;
    about)
      FILE="app/templates/partials/about_section.html"
      BLOCK="{# --- Full About + Mission Block (mosaic, counters, video modal) --- #}
<section id='fc-about' class='relative bg-fc-surface py-16 sm:py-24 text-fc-text'>
  <div class='max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-10'>
    <div>
      <h2 class='text-3xl md:text-4xl font-bold mb-4'>Our Mission</h2>
      <p class='mb-6'>We’re building more than a basketball program — we’re shaping leaders, scholars, and role models in the Austin community.</p>
      <ul class='space-y-3'>
        <li>🏀 <strong>15–3</strong> Regionals record</li>
        <li>🏆 <strong>3 Championships</strong> last season</li>
        <li>🎓 <strong>Top 1% academic athletes</strong></li>
      </ul>
    </div>
    <div class='grid grid-cols-2 gap-4'>
      <img src='{{ url_for(\"static\", filename=\"images/player1.webp\") }}' class='rounded-xl object-cover'>
      <img src='{{ url_for(\"static\", filename=\"images/player2.webp\") }}' class='rounded-xl object-cover'>
      <img src='{{ url_for(\"static\", filename=\"images/player3.webp\") }}' class='rounded-xl object-cover'>
      <button class='col-span-2 bg-fc-brand text-black py-2 rounded-lg hover:opacity-90' data-modal-target='video-modal'>▶ Watch Our Story</button>
    </div>
  </div>
</section>"
      ;;
    header)
      FILE="app/templates/partials/header_and_announcement.html"
      BLOCK="{# --- Full Header Block (mini meter + socket ticker) --- #}
<header id='fc-header' class='sticky top-0 z-50 bg-fc-bg/95 backdrop-blur'>
  <div class='max-w-7xl mx-auto px-6 flex justify-between items-center py-4'>
    <a href='/' class='flex items-center space-x-2'>
      <img src='{{ team.logo|default(url_for(\"static\", filename=\"images/logo.webp\")) }}' alt='{{ team_name }} logo' class='h-10 w-10 rounded-full'>
      <span class='font-bold'>{{ team_name }}</span>
    </a>
    <div id='hdr-meter' class='flex items-center space-x-2 text-sm'>
      <span id='hdr-raised'>\${{ \"{:,.0f}\".format(funds_raised) }}</span> /
      <span id='hdr-goal'>\${{ \"{:,.0f}\".format(fundraising_goal) }}</span>
      <div class='w-24 bg-white/20 h-2 rounded overflow-hidden'>
        <div id='hdr-pct' class='h-2 bg-[{{ theme_hex }}]' style='width: {{ pct }}%'></div>
      </div>
    </div>
  </div>
</header>"
      ;;
    footer)
      FILE="app/templates/partials/footer.html"
      BLOCK="<footer id='fc-footer' class='bg-fc-surface text-fc-text py-12 text-center'>
  <p class='mb-4'>Want to make a bigger impact? Become a sponsor today!</p>
  <a href='/sponsor' class='bg-fc-brand text-black px-6 py-3 rounded-lg font-semibold hover:opacity-90'>Become a Sponsor</a>
  <div class='mt-6 text-sm opacity-70'>© {{ now().year }} FundChamps — All rights reserved.</div>
</footer>"
      ;;
    *)
      echo "❌ Unknown partial: $name"
      continue
      ;;
  esac

  if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    continue
  fi

  cp "$FILE" "$FILE.bak.$TS"
  echo "→ Patching $FILE ..."
  printf "%s\n" "$BLOCK" > "$FILE"
  echo "✅ Patched: $name ($FILE)"
done


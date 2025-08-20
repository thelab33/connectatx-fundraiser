#!/usr/bin/env bash
set -euo pipefail

# --- paths ---
CSS="app/static/css/header-safe.css"
JS="app/static/js/header-safe.js"
TPL_DIR="app/templates"
# try to find your base/layout file that has </head> and </body>
BASE_FILE="$(grep -RIl '</head>' "$TPL_DIR" | head -1 || true)"

[[ -z "${BASE_FILE:-}" ]] && { echo "❌ Could not find a base layout (file with </head>). Edit BASE_FILE."; exit 1; }

# --- write CSS (zero-risk polish) ---
mkdir -p "$(dirname "$CSS")"
cat > "$CSS" <<'CSS'
:root { --fc-accent: var(--fc-hero-accent, #facc15) }
#site-header[data-sticky-header], [id^="site-header"][data-sticky-header] { isolation:isolate }
#site-header .hdr-nav a{ text-underline-offset: 3px }
#site-header.is-shrunk .shrinkable{ transform:scale(.97); opacity:.98; transition:transform .15s ease,opacity .15s ease }
#hdr-meter .track{ background:rgba(255,255,255,.12); border-radius:9999px; overflow:hidden }
#hdr-meter .fill{ height:6px; width:0%; background:linear-gradient(90deg,#fde68a,var(--fc-accent),#f59e0b); transition:width .6s cubic-bezier(.22,1,.36,1) }
:where(a,button,[tabindex],input,select,textarea):focus-visible{
  outline:3px solid color-mix(in srgb, var(--fc-accent) 75%, transparent); outline-offset:3px
}
CSS

# --- write JS (hooks into existing meter/events) ---
mkdir -p "$(dirname "$JS")"
cat > "$JS" <<'JS'
(()=>{try{
  const d=document, header=d.querySelector('#site-header,[data-sticky-header]')?.closest('header')||d.querySelector('header');
  // shrink on scroll (IO when possible)
  const sentinel=d.getElementById('site-header-sentinel')||d.createElement('div');
  if(!sentinel.isConnected){ sentinel.id='site-header-sentinel'; header?.before(sentinel); }
  if('IntersectionObserver'in window){
    new IntersectionObserver(([e])=>{
      header?.classList.toggle('is-shrunk', !e.isIntersecting);
    },{rootMargin:'-56px 0px 0px 0px'}).observe(sentinel);
  }
  // mini meter sync
  const fill=d.querySelector('#hdr-meter .fill')||d.querySelector('#hdr-bar');
  const pctLbl=d.querySelector('#hdr-meter [data-hdr-pct],#hdr-pct');
  const raisedLbl=d.querySelector('#hdr-raised'); const goalLbl=d.querySelector('#hdr-goal');
  const nf=new Intl.NumberFormat(undefined,{maximumFractionDigits:0});
  const fmt$=n=>'$'+nf.format(Math.round(+n||0));
  function setMeter(raised,goal){
    if(!(goal>0)) return;
    const p=Math.max(0,Math.min(100,(raised/goal)*100));
    if(fill) fill.style.width=p.toFixed(1)+'%';
    if(pctLbl) pctLbl.textContent=p.toFixed(0)+'%';
    if(raisedLbl) raisedLbl.textContent=fmt$(raised);
    if(goalLbl) goalLbl.textContent=fmt$(goal);
  }
  // listen for the app's live events
  addEventListener('fc:funds:update',e=>{
    const {raised,goal}=e.detail||{}; if(typeof raised==='number'&&typeof goal==='number') setMeter(raised,goal);
  },{passive:true});
  // initial pull (non-blocking)
  const url=header?.dataset.statsUrl||'/api/stats';
  (async()=>{ try{
    const r=await fetch(url,{headers:{Accept:'application/json'}});
    if(r.ok){ const j=await r.json(); setMeter(j.raised??j.funds_raised, j.goal??j.fundraising_goal); }
  }catch{} })();
  // set theme-color to accent for mobile UI
  let meta=d.querySelector('meta[name=theme-color]'); if(!meta){ meta=d.createElement('meta'); meta.name='theme-color'; d.head.appendChild(meta); }
  const col=(getComputedStyle(d.documentElement).getPropertyValue('--fc-hero-accent')||'#facc15').trim();
  meta.setAttribute('content',col);
}catch(e){}})();
JS

# --- inject into base layout (idempotent) ---
cp "$BASE_FILE" "$BASE_FILE.bak.$(date +%F-%H%M)"
grep -q 'header-safe.css' "$BASE_FILE" || sed -i.bak '/<\/head>/i \ \ \ \ <link rel="stylesheet" href="{{ url_for('\''static'\'', filename='\''css/header-safe.css'\'') }}">' "$BASE_FILE"
grep -q 'header-safe.js' "$BASE_FILE"   || sed -i.bak '/<\/body>/i \ \ \ \ <script src="{{ url_for('\''static'\'', filename='\''js/header-safe.js'\'') }}" nonce="{{ NONCE|default('\'''\'') }}"></script>' "$BASE_FILE"

echo "✅ Patched:"
echo "  • $CSS"
echo "  • $JS"
echo "  • Injected into -> $BASE_FILE"


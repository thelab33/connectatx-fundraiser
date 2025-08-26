#!/usr/bin/env bash
set -euo pipefail

echo "╭──────────────────────────────────────────────╮"
echo "│  🏆 Starforge Tiers Patch — FundChamps Elite │"
echo "╰──────────────────────────────────────────────╯"

BASE=${BASE:-app/templates/base.html}
TS=$(date +%Y%m%d-%H%M%S)

# Fallback locate base.html if missing
if [ ! -f "$BASE" ]; then
  BASE=$(grep -RIl --exclude="*.bak*" --include="*.html" "</head>" app/templates | head -1 || true)
fi
[ -z "$BASE" ] && { echo "❌ Could not locate base.html"; exit 1; }

echo "→ Target base template: $BASE"

# --- Install CSS ---
CSS_FILE="app/static/css/tiers-elite.css"
mkdir -p "$(dirname "$CSS_FILE")"
cat > "$CSS_FILE" <<'CSS'
:root{--tier-accent:var(--fc-hero-accent,#facc15)}
#tiers .s-tier-card{position:relative;border-radius:16px;background:rgba(255,255,255,.05);backdrop-filter:blur(6px) saturate(1.05);-webkit-backdrop-filter:blur(6px) saturate(1.05);border:1px solid rgba(255,255,255,.08);box-shadow:0 10px 30px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.06)}
#tiers .s-tier-card:hover{transform:translateY(-2px);transition:transform .18s ease}
#tiers .s-tier-badge{position:absolute;top:10px;right:10px;font-size:12px;padding:4px 8px;border-radius:9999px;background:color-mix(in srgb,var(--tier-accent) 85%, transparent);color:#0b0b0c;border:1px solid rgba(255,255,255,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}
#tiers .s-tier-cta{outline:2px solid color-mix(in srgb,var(--tier-accent) 55%, transparent);outline-offset:2px}
#tiers .s-tier-card.in-view{animation:tiersPop .35s cubic-bezier(.2,.9,.2,1)}
@keyframes tiersPop{0%{transform:translateY(8px);opacity:.0}100%{transform:none;opacity:1}}
#tiers-sticky{position:fixed;left:0;right:0;bottom:12px;z-index:55;display:none;place-items:center}
#tiers-sticky .wrap{background:rgba(12,12,13,.9);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.10);border-radius:9999px;padding:6px 12px;color:#fff;box-shadow:0 8px 30px rgba(0,0,0,.45)}
#tiers-sticky.show{display:grid}
CSS

# --- Install JS ---
JS_FILE="app/static/js/tiers-elite.js"
mkdir -p "$(dirname "$JS_FILE")"
cat > "$JS_FILE" <<'JS'
(()=>{try{
  const d=document,cards=[...d.querySelectorAll("#tiers .s-tier-card")];
  if(!cards.length) return;
  const emoji={gold:"🥇",silver:"🥈",bronze:"🥉"};
  cards.forEach(card=>{
    const m=card.dataset.tier||"";
    if(!card.querySelector(".s-tier-badge")){
      const b=d.createElement("span"); b.className="s-tier-badge";
      b.textContent=emoji[m]+" "+m.charAt(0).toUpperCase()+m.slice(1); card.appendChild(b);
    }
    card.querySelectorAll("a,button").forEach(btn=>{
      if(/sponsor/i.test(btn.textContent)){
        btn.classList.add("s-tier-cta");
        btn.addEventListener("click",()=>{ try{ localStorage.setItem("fc_last_tier",m);}catch(e){} showSticky(m); });
      }
    });
  });
  function showSticky(name){
    let bar=d.getElementById("tiers-sticky");
    if(!bar){ bar=d.createElement("div"); bar.id="tiers-sticky"; bar.innerHTML='<div class="wrap">Selected: <b></b></div>'; d.body.appendChild(bar); }
    bar.querySelector("b").textContent=name; bar.classList.add("show"); setTimeout(()=>bar.classList.remove("show"),2200);
  }
  const want=(new URLSearchParams(location.search).get("tier")||(localStorage.getItem("fc_last_tier")||"")).toLowerCase();
  if(want){ const hit=cards.find(c=>c.dataset.tier===want); if(hit) hit.classList.add("in-view"); }
  if("IntersectionObserver" in window){
    const io=new IntersectionObserver(ents=>ents.forEach(e=>{ e.target.classList.toggle("in-view", e.isIntersecting); }),{threshold:.15});
    cards.forEach(c=>io.observe(c));
  }
}catch(e){}})();
JS

# --- Backup + Inject into base.html ---
cp "$BASE" "$BASE.bak.$TS"

grep -q "tiers-elite.css" "$BASE" || \
  sed -i "/<\/head>/i \ \ \ \ <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/tiers-elite.css') }}\">" "$BASE"

grep -q "tiers-elite.js" "$BASE" || \
  sed -i "/<\/body>/i \ \ \ \ <script src=\"{{ url_for('static', filename='js/tiers-elite.js') }}\" nonce=\"{{ NONCE|default('') }}\"></script>" "$BASE"

echo "✅ Tiers pack installed successfully."


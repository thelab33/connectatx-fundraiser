#!/usr/bin/env bash
set -euo pipefail

HERO="app/templates/partials/hero_and_fundraiser.html"
TS="$(date +%Y%m%d-%H%M%S)"

[[ -f "$HERO" ]] || { echo "❌ $HERO not found"; exit 1; }
cp "$HERO" "$HERO.bak.$TS"

python3 - <<'PY'
import re, pathlib
p=pathlib.Path("app/templates/partials/hero_and_fundraiser.html")
t=p.read_text()

# 1) Replace openCheckout(...) with fcStripeRedirect(...)
t=re.sub(r"\bopenCheckout\s*\(", "fcStripeRedirect(", t)

# 2) Inject flex JS/CSS + JSON-LD once, just before </section>
if "window.__fcFlexInit" not in t:
  inject = r"""
  <script nonce="{{ NONCE }}">
  // --- FC FLEX: Stripe redirect + VIP toast + ticker + JSON-LD ---
  (()=>{ if(window.__fcFlexInit)return; window.__fcFlexInit=true;
    const $=(s,r=document)=>r.querySelector(s);
    const ticker=$('#fc-ticker'); const toastRoot=document.body;

    async function getPaymentsConfig(){
      try{
        const r=await fetch('/api/payments/config',{headers:{'accept':'application/json'}});
        if(!r.ok) throw 0; return await r.json();
      }catch{ return {}; }
    }

    async function fcStripeRedirect(amount){
      const cfg=await getPaymentsConfig();
      const link=cfg.payment_link_url||cfg.link||null;
      const hasPK=!!(cfg.publishable_key||cfg.pk||'');
      const cents=Math.max(0,Math.round((Number(amount)||0)*100));
      if(hasPK && link){
        const url=link+(link.includes('?')?'&':'?')+'client_reference_id='+encodeURIComponent(String(cents||0));
        location.assign(url); return;
      }
      location.assign('/donate?amount=' + encodeURIComponent(String(amount||0)));
    }
    window.fcStripeRedirect=fcStripeRedirect;

    // Wire quick amounts + big donate
    document.querySelectorAll('[data-amount]').forEach(btn=>{
      btn.addEventListener('click',()=>fcStripeRedirect(Number(btn.getAttribute('data-amount'))||0),{passive:true});
    });
    $('#fc-donate')?.addEventListener('click',()=>fcStripeRedirect(0),{passive:true});

    // VIP toast + ticker append (listen for `fc:vip:hit`)
    function toast(msg){
      const el=document.createElement('div');
      el.className='fc-toast'; el.role='status'; el.textContent=msg;
      toastRoot.appendChild(el);
      requestAnimationFrame(()=>{ el.classList.add('show');
        setTimeout(()=>{ el.classList.remove('show'); setTimeout(()=>el.remove(),400); },3800);
      });
    }
    window.addEventListener('fc:vip:hit',e=>{
      const d=e.detail||{}; const name=d.name||'VIP Donor'; const amt=d.amount||0; const tier=d.tier||'VIP';
      toast(`🏆 ${name} just gave $${(amt||0).toLocaleString()} — ${tier}!`);
      if(ticker){
        const s=document.createElement('span');
        s.className='mx-6 text-xs text-zinc-300'; s.textContent=`🏅 ${name}`;
        ticker.appendChild(s.cloneNode(true));
      }
    });

    // JSON-LD DonateAction (SEO)
    try{
      const data={
        "@context":"https://schema.org","@type":"DonateAction",
        "name":"Donate to {{ team_name|e }}",
        "description":"Support {{ team_name|e }} fundraising.",
        "agent":{"@type":"SportsTeam","name":"{{ team_name|e }}"},
        "actionStatus":"PotentialActionStatus",
        "target":{"@type":"EntryPoint","urlTemplate":"{{ url_for('main.donate', _external=True) }}",
          "actionPlatform":["http://schema.org/DesktopWebPlatform","http://schema.org/MobileWebPlatform"]}
      };
      const s=document.createElement('script');
      s.type='application/ld+json'; s.setAttribute('nonce','{{ NONCE }}');
      s.textContent=JSON.stringify(data); document.head.appendChild(s);
    }catch{}
  })();
  </script>
  <style nonce="{{ NONCE }}">
    .fc-toast{position:fixed;right:12px;bottom:12px;background:rgba(34,197,94,.95);
      color:#0b0b0c;font-weight:700;padding:.6rem .8rem;border-radius:.75rem;
      box-shadow:0 10px 30px rgba(0,0,0,.3);transform:translateY(12px);opacity:0;
      transition:transform .25s ease,opacity .25s ease;z-index:80;}
    .fc-toast.show{transform:translateY(0);opacity:1;}
  </style>
"""
  t=re.sub(r"</section>\s*$", inject+"\n</section>", t, flags=re.S)

p.write_text(t)
print("OK: hero flex injected/rewired")
PY

# Also rewire any other partial still calling openCheckout(...)
echo "🔁 Scanning other partials for openCheckout(...)"
grep -RIl "openCheckout(" app/templates/partials || true | while read -r F; do
  cp "$F" "$F.bak.$TS"
  sed -E -i 's/\bopenCheckout\s*\(/fcStripeRedirect(/g' "$F"
  echo "  → $F"
done

echo "✅ Flex patch complete."


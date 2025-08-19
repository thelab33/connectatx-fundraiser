#!/usr/bin/env python3
"""
FundChamps • Hero & Fundraiser SV-Elite Auto-Enhancer
- Creates/updates app/templates/partials/hero_and_fundraiser.html
- Safely rewires base/index to include the hero partial (idempotent)
- Backs up originals with timestamped .bak
"""
from __future__ import annotations
import re, sys, shutil
from pathlib import Path
from datetime import datetime

SENTINEL = "<!-- FC:HERO_SV_ELITE -->"

HERO_SV_ELITE = """<!-- FC:HERO_SV_ELITE -->
{# ========================================================================
   hero_and_fundraiser.html — SV Centered, Pro-Polished, CSP-safe
   - Centered headline with contrast plate + tiny stroke
   - Larger hero height; stronger top gradient for readability
   - Slim chips aligned with progress; milestone hint; Web Share
   - Keeps window.updateHeroMeter() & window.getHeroMeter()
   ======================================================================== #}
{% set NONCE     = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}
{% set theme_hex = theme_hex|default('#facc15') %}
{% set team_name = (team.team_name if team and team.team_name else 'Connect ATX Elite') %}
{% set HERO_TITLE = 'Connect ATX Elite — Fundraiser' %}

{# --- Numbers (robust to "$12,345") --- #}
{% set _fr = (funds_raised|string)|replace('$','')|replace(',','')|float if funds_raised is defined else 0.0 %}
{% set _fg = (fundraising_goal|string)|replace('$','')|replace(',','')|float if fundraising_goal is defined and fundraising_goal else 10000.0 %}
{% set funds_raised = _fr %}
{% set fundraising_goal = (_fg if _fg > 0 else 1.0) %}
{% set pct_raw = 100.0 * (funds_raised / (fundraising_goal if fundraising_goal else 1)) %}
{% set pct = (0 if pct_raw < 0 else (100 if pct_raw > 100 else pct_raw)) | round(1) %}

{# --- Background (team > fallbacks) --- #}
{% set _input_src = (
  (team.hero_bg if team and team.hero_bg is defined and team.hero_bg) or
  (team.hero_image if team and team.hero_image is defined and team.hero_image) or
  (team.team_photo if team and team.team_photo is defined and team.team_photo) or
  (team.photo_url  if team and team.photo_url  is defined and team.photo_url) or
  none
) %}
{% set _default_jpg        = 'images/connect-atx-team.jpg' %}
{% set _default_logo_webp  = 'images/logo.webp' %}
{% set _default_logo_avif  = 'images/logo.avif' %}

{% if _input_src %}
  {% if '://' in _input_src or _input_src.startswith('data:') %}
    {% set hero_bg = _input_src %}
  {% else %}
    {% set hero_bg = (url_for('static', filename=_input_src.lstrip('/')) if url_for is defined else '/' ~ _input_src.lstrip('/')) %}
  {% endif %}
  {% set hero_bg_avif = none %}
  {% set hero_bg_webp = none %}
{% else %}
  {% if url_for is defined %}
    {% set hero_bg      = url_for('static', filename=_default_jpg) %}
    {% set hero_bg_webp = none %}
    {% set hero_bg_avif = none %}
    {% set hero_fallback= url_for('static', filename=_default_logo_webp) %}
  {% else %}
    {% set hero_bg      = '/static/' ~ _default_jpg %}
    {% set hero_bg_webp = none %}
    {% set hero_bg_avif = none %}
    {% set hero_fallback= '/static/' ~ _default_logo_webp %}
  {% endif %}
{% endif %}
{% if not hero_fallback %}
  {% set hero_fallback = (url_for('static', filename=_default_logo_webp) if url_for is defined else '/static/' ~ _default_logo_webp) %}
{% endif %}
{% set logo_avif = (url_for('static', filename=_default_logo_avif) if url_for is defined else '/static/' ~ _default_logo_avif) %}

{# --- Other knobs --- #}
{% set fundraiser_deadline   = fundraiser_deadline if fundraiser_deadline is defined and fundraiser_deadline else '2025-12-31T23:59:59' %}
{% set quick_donate_amounts  = quick_donate_amounts if quick_donate_amounts is defined and quick_donate_amounts else [25,50,100,250] %}
{% set stripe_publishable_key= stripe_publishable_key|default('') %}
{% set sponsors              = sponsors if sponsors is defined and sponsors else ['Austin Realty','TechNova','River BBQ','Sunrise Dental'] %}
{% set sponsor_list_href     = sponsor_list_href if sponsor_list_href is defined and sponsor_list_href else '/sponsors' %}
{% set become_sponsor_href   = become_sponsor_href if become_sponsor_href is defined and become_sponsor_href else '/become-sponsor' %}
{% set donate_href           = donate_href if donate_href is defined and donate_href else '/donate' %}
{% set vip_thresholds        = vip_thresholds if vip_thresholds is defined and vip_thresholds else [5000, 10000, 20000] %}
{% set goal_heat_enabled     = goal_heat_enabled if goal_heat_enabled is defined else true %}
{% set ab_copy               = ab_copy if ab_copy is defined and ab_copy else ["Your $25 covers 1 practice", "$25 = 1 practice pass"] %}

{# --- Brand tail + focal point --- #}
{% set BRAND = 'Connect ATX Elite' %}
{% set show_brand_tail = (team_name|lower != BRAND|lower) %}
{% set hero_focus = (team.hero_focus if team and team.hero_focus is defined and team.hero_focus else '50% 24%') %}

<section id="fc-hero"
         class="relative overflow-clip min-h-[82vh] sm:min-h-[88vh]"
         aria-labelledby="fc-hero-title"
         style="--fc-hero-accent: {{ theme_hex }}; --hero-offset: clamp(3.25rem, 12vw, 10rem);">
  <!-- Background -->
  <div class="absolute inset-0">
    <picture>
      {% if hero_bg_avif %}<source srcset="{{ hero_bg_avif }}" type="image/avif" sizes="100vw">{% endif %}
      {% if hero_bg_webp %}<source srcset="{{ hero_bg_webp }}" type="image/webp" sizes="100vw">{% endif %}
      <img id="fc-hero-img"
           src="{{ hero_bg }}"
           data-fallback="{{ hero_fallback }}"
           alt="{{ team_name }} team photo"
           width="1920" height="1080"
           class="h-full w-full object-cover opacity-0 will-change-[filter,opacity]"
           style="object-position: {{ hero_focus }};"
           loading="eager" decoding="async" fetchpriority="high" sizes="100vw">
    </picture>
    <div class="fc-hero-grad" aria-hidden="true"></div>
    <div class="fc-hero-glow" aria-hidden="true"></div>
    <div class="heat-layer"   aria-hidden="true"></div>
    <div class="noise-layer mix-blend-soft-light" aria-hidden="true"></div>
  </div>

  <!-- Content (centered, offset into photo) -->
  <div class="relative fc-section">
    <div class="mx-auto fc-hero-card rounded-3xl p-5 sm:p-7 lg:p-8 max-w-7xl relative z-[1]"
         style="margin-top: var(--hero-offset);">
      <!-- Headline -->
      <div class="flex flex-col items-center text-center gap-3 sm:gap-4">
        <div class="fc-title-wrap">
          <h1 id="fc-hero-title"
              class="fc-title-glow text-3xl sm:text-5xl lg:text-6xl font-extrabold leading-tight tracking-tight">
            <span class="inline-block bg-clip-text text-transparent fc-hero-title-gradient fc-title-text">
              {{ team_name }}
            </span>
            {% if show_brand_tail %}
              <span class="ml-1 opacity-90">{{ BRAND }}</span>
            {% else %}
              <span class="ml-2 align-top text-lg sm:text-xl text-zinc-300/90">— Fundraiser</span>
            {% endif %}
          </h1>
        </div>

        <p id="fc-ab-copy"
           class="text-[13px] sm:text-base text-zinc-50/95 bg-black/35 backdrop-blur px-3 py-1 rounded-full ring-1 ring-white/10">
          Every dollar fuels travel, uniforms, and training. You’re part of the story.
        </p>

        <!-- Countdown (compact) -->
        <div class="grid grid-cols-4 gap-2 text-center select-none"
             role="timer" aria-live="polite" aria-describedby="fc-deadline">
          {% for key in ['Days','Hrs','Min','Sec'] %}
          <div class="rounded-lg bg-white/5 ring-1 ring-white/10 px-2 py-1.5 sm:px-3 sm:py-2">
            <div class="fc-ct-num text-lg sm:text-2xl font-bold tabular-nums" id="fc-ct-{{ key|lower }}">00</div>
            <div class="text-[10px] sm:text-[11px] uppercase tracking-wider text-zinc-300">{{ key }}</div>
          </div>
          {% endfor %}
        </div>
      </div>

      <!-- Body -->
      <div class="mt-5 sm:mt-7 grid lg:grid-cols-5 items-stretch gap-5">
        <!-- Progress -->
        <section class="lg:col-span-3 h-full flex flex-col" aria-labelledby="fc-progress-title">
          <div class="flex-1 rounded-2xl p-4 sm:p-5 ring-1 ring-white/10 bg-gradient-to-br from-white/5 to-white/0">
            <h2 id="fc-progress-title" class="sr-only">Fundraising progress</h2>

            <div class="flex items-end justify-between gap-4">
              <div>
                <div class="text-zinc-300 text-xs sm:text-sm">Raised</div>
                <div class="text-2xl sm:text-4xl font-extrabold tabular-nums" id="fc-raised" aria-live="polite">
                  ${{ ('%0.0f' % funds_raised) }}
                </div>
              </div>
              <div class="text-right">
                <div class="text-zinc-300 text-xs sm:text-sm">Goal</div>
                <div class="text-lg sm:text-2xl font-semibold tabular-nums" id="fc-goal">
                  ${{ ('%0.0f' % fundraising_goal) }}
                </div>
              </div>
            </div>

            <div class="mt-3">
              <!-- Progressbar -->
              <div class="relative h-3 sm:h-4 w-full rounded-full bg-zinc-800/70 ring-1 ring-white/10 overflow-hidden"
                   role="progressbar" aria-valuemin="0" aria-valuemax="100"
                   aria-valuenow="{{ ('%.1f' % pct) }}"
                   aria-label="Fundraising progress toward goal">
                <div class="fc-shine absolute inset-0"></div>
                <div id="fc-bar" class="h-full rounded-full fc-bar" style="width: {{ pct }}%;"></div>
              </div>

              <!-- Milestones -->
              <div class="relative mt-2 sm:mt-3 flex justify-between text-[10px] sm:text-[11px] text-zinc-300">
                {% for m in [25,50,75,100] %}
                  <div class="group relative flex-1">
                    <div class="h-2 sm:h-3 w-px mx-auto bg-white/20" aria-hidden="true"></div>
                    <div class="absolute -top-6 sm:-top-7 left-1/2 -translate-x-1/2">
                      <span class="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 sm:px-2 sm:py-1 ring-1 ring-white/10 bg-white/5 group-[.active]:bg-white/10 group-[.active]:text-white"
                            id="fc-ms-{{ m }}" aria-label="{{ m }} percent milestone">
                        <span class="hidden sm:inline">Milestone</span> {{ m }}%
                      </span>
                    </div>
                  </div>
                {% endfor %}
              </div>

              <div class="mt-2 sm:mt-3 flex items-center justify-between">
                <div class="text-xs sm:text-sm text-zinc-300">
                  <span class="sr-only">Progress:</span>
                  <span id="fc-pct" class="font-semibold tabular-nums">{{ ('%.1f' % pct) }}</span>% funded
                </div>
                <div class="text-xs sm:text-sm text-zinc-300">
                  Deadline: <time id="fc-deadline" datetime="{{ fundraiser_deadline }}">{{ fundraiser_deadline }}</time>
                </div>
              </div>

              <!-- Next milestone hint -->
              <div id="fc-next" class="mt-1.5 sm:mt-2 text-[11px] sm:text-xs text-zinc-400"></div>
            </div>
          </div>
        </section>

        <!-- Quick actions -->
        <aside class="lg:col-span-2 h-full flex flex-col" aria-labelledby="fc-quick-actions">
          <div class="flex-1 rounded-2xl p-4 sm:p-5 ring-1 ring-white/10 bg-white/5 flex flex-col gap-3 sm:gap-4">
            <h2 id="fc-quick-actions" class="sr-only">Quick actions</h2>

            <div class="grid grid-cols-2 gap-2">
              {% for amt in quick_donate_amounts %}
              <button type="button"
                      class="fc-cta rounded-2xl px-3 py-2.5 sm:py-3 text-xl sm:text-2xl font-extrabold tabular-nums leading-none
                             bg-white/[.06] hover:bg-white/[.10] ring-1 ring-white/15
                             shadow-[inset_0_0_0_1px_rgba(255,255,255,.06)]
                             transition"
                      style="color:#0b0b0c; background: color-mix(in srgb, var(--fc-hero-accent, {{ theme_hex }}) 92%, transparent);
                             text-shadow: 0 1px 0 rgba(255,255,255,.35);"
                      data-amount="{{ amt }}"
                      aria-label="Quick donate {{ amt }} dollars">
                ${{ amt }}
              </button>
              {% endfor %}
            </div>

            <!-- Share -->
            <div class="flex items-center justify-between -mt-0.5">
              <a id="fc-share"
                 href="{{ sponsor_list_href }}"
                 class="inline-flex items-center gap-1 text-[13px] sm:text-sm text-yellow-200/90 hover:text-yellow-200 underline underline-offset-2">
                 🔗 Share
              </a>
              <span id="fc-share-ok" class="text-xs text-emerald-300 hidden">Link copied</span>
            </div>

            <div class="flex gap-2">
              <button type="button" id="fc-donate"
                      class="flex-1 rounded-xl px-4 py-2.5 sm:py-3 font-semibold bg-white/10 hover:bg-white/15 ring-1 ring-white/10">
                💸 Quick Donate
              </button>
              <a href="{{ become_sponsor_href }}"
                 class="rounded-xl px-4 py-2.5 sm:py-3 font-semibold bg-emerald-500/90 hover:bg-emerald-500">
                🤝 Become a Sponsor
              </a>
            </div>

            <!-- Trust flip -->
            <div class="relative mt-1 h-11 sm:h-12 [perspective:1000px]" aria-hidden="true">
              <div class="absolute inset-0 [transform-style:preserve-3d] transition-transform duration-700 hover:[transform:rotateY(180deg)]">
                <div class="absolute inset-0 grid place-items-center rounded-xl ring-1 ring-white/10 bg-white/5 [backface-visibility:hidden]">
                  <span class="text-[11px] sm:text-xs text-zinc-300">Payments Secured • PCI-DSS</span>
                </div>
                <div class="absolute inset-0 grid place-items-center rounded-xl ring-1 ring-white/10 bg-white/5 [transform:rotateY(180deg)] [backface-visibility:hidden]">
                  <span class="text-[11px] sm:text-xs text-zinc-200">
                    {% if stripe_publishable_key %}Secured by Stripe{% else %}PayPal / Card{% endif %}
                  </span>
                </div>
              </div>
            </div>

            <!-- Ticker -->
            <div class="relative overflow-hidden rounded-xl ring-1 ring-white/10 bg-white/5">
              <div class="ticker-row whitespace-nowrap will-change-transform py-1.5" id="fc-ticker" aria-label="Sponsor ticker">
                {% for s in sponsors %}<span class="mx-6 text-xs text-zinc-300">🏅 {{ s }}</span>{% endfor %}
                {% for s in sponsors %}<span class="mx-6 text-xs text-zinc-300">🏅 {{ s }}</span>{% endfor %}
              </div>
            </div>
          </div>
        </aside>
      </div>

      <div class="mt-5 sm:mt-6 grid sm:grid-cols-3 gap-2.5 sm:gap-3 text-center">
        <div class="rounded-xl ring-1 ring-white/10 bg-white/5 px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-zinc-300">🎯 Goal tracking in real-time</div>
        <div class="rounded-xl ring-1 ring-white/10 bg-white/5 px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-zinc-300">🔒 Secure checkout</div>
        <div class="rounded-xl ring-1 ring-white/10 bg-white/5 px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-zinc-300">✨ VIP shout-outs for top donors</div>
      </div>
    </div>
  </div>

  <noscript>
    <div class="absolute bottom-3 left-3 text-xs text-zinc-300 bg-black/50 px-2 py-1 rounded">
      JavaScript disabled: live meter & countdown paused.
    </div>
  </noscript>

  <style nonce="{{ NONCE }}">
    /* Stronger readability for the gradient title */
    #fc-hero .fc-title-wrap{ position:relative; display:inline-block; }
    #fc-hero .fc-title-wrap::before{
      content:""; position:absolute; inset:-.35rem -.9rem; border-radius:1.25rem;
      background:
        radial-gradient(60% 70% at 50% 45%, rgba(0,0,0,.62), transparent 78%),
        linear-gradient(to bottom, rgba(0,0,0,.20), transparent 60%);
      filter: blur(8px); z-index:-1;
    }
    #fc-hero .fc-title-text{ letter-spacing:-.02em; }
    @supports(-webkit-text-stroke:1px black){
      #fc-hero .fc-title-text{ -webkit-text-stroke:.6px rgba(0,0,0,.55); }
    }

    /* Title glow */
    #fc-hero .fc-title-glow{
      text-shadow:
        0 1px 0 rgba(0,0,0,.60),
        0 16px 40px rgba(0,0,0,.45),
        0 0 26px color-mix(in oklab, var(--fc-hero-accent, {{ theme_hex }}) 30%, transparent);
    }

    /* Slightly darker top gradient via vars */
    #fc-hero{
      --hero-grad-top:.52;  /* was .40 */
      --hero-grad-mid:.26;  /* was .22 */
      --hero-grad-bot:.78;  /* was .72 */
    }

    /* LCP-friendly reveal on hero image */
    #fc-hero #fc-hero-img{ transition: opacity .45s ease; }
  </style>

  {% if script_open is defined %}{{ script_open() }}{% else %}<script nonce="{{ NONCE }}">{% endif %}
  (() => {
    if (window.__fcHeroInit) return; window.__fcHeroInit = true;

    const VIPS = {{ vip_thresholds|tojson|safe }};
    const HEAT_ON = {{ 'true' if goal_heat_enabled else 'false' }};
    const AB_COPY = {{ ab_copy|tojson|safe }};

    const $  = (s,r=document)=>r.querySelector(s);
    const $$ = (s,r=document)=>Array.from(r.querySelectorAll(s));
    const clamp=(n,min,max)=>Math.min(Math.max(n,min),max);
    const fmtMoney=v=>new Intl.NumberFormat(undefined,{style:'currency',currency:'USD',maximumFractionDigits:0}).format(+v||0);

    const els = {
      img: $('#fc-hero-img'), bar: $('#fc-bar'), raised: $('#fc-raised'), goal: $('#fc-goal'),
      pct: $('#fc-pct'), next: $('#fc-next'),
      countdown:{days:$('#fc-ct-days'),hrs:$('#fc-ct-hrs'),min:$('#fc-ct-min'),sec:$('#fc-ct-sec')},
      ticker: $('#fc-ticker'), root: $('#fc-hero'), ab: $('#fc-ab-copy'),
      progressWrap: $('[role="progressbar"]'), share: $('#fc-share'), shareOK: $('#fc-share-ok')
    };

    // LCP-safe reveal + fallback
    try{
      const reveal = ()=> { if(els.img) els.img.style.opacity='1'; };
      els.img?.addEventListener('load', reveal, { once:true });
      els.img?.addEventListener('error', () => {
        const fb = els.img?.getAttribute('data-fallback');
        if (fb && els.img?.src !== fb) els.img.src = fb;
        reveal();
      }, { once:true });
    }catch{}

    const state = {
      raised: {{ funds_raised|float }},
      goal: Math.max(1, {{ fundraising_goal|float }}),
      deadline: new Date('{{ fundraiser_deadline }}'),
    };

    const burstConfetti = (function(){return function(n=24){try{
      const c=document.createElement('canvas');c.width=innerWidth;c.height=240;
      Object.assign(c.style,{position:'fixed',left:0,top:0,pointerEvents:'none',zIndex:60});
      document.body.appendChild(c);
      const ctx=c.getContext('2d');
      const p=Array.from({length:n}).map(()=>({x:Math.random()*c.width,y:-20-Math.random()*60,vx:(Math.random()-.5)*3,vy:2+Math.random()*3,r:2+Math.random()*4,a:1}));
      const accent=getComputedStyle(document.documentElement).getPropertyValue('--fc-hero-accent').trim()||'{{ theme_hex }}';
      const colors=['#ffffff',accent,'#22c55e','#60a5fa','#eab308'];
      (function tick(){
        ctx.clearRect(0,0,c.width,c.height);
        p.forEach(o=>{o.x+=o.vx;o.y+=o.vy;o.a-=.012;ctx.globalAlpha=Math.max(0,o.a);
          ctx.fillStyle=colors[(Math.random()*colors.length)|0];ctx.beginPath();ctx.arc(o.x,o.y,o.r,0,2*Math.PI);ctx.fill();});
        if(p.some(o=>o.a>0)) requestAnimationFrame(tick); else c.remove();
      })();
    }catch{}}})();

    function tweenNumber(el,to,dur=700){
      if(!el) return;
      const from=parseFloat((el.textContent||'0').replace(/[^0-9.-]/g,''))||0;
      const start=performance.now();
      (function step(t){
        const k=Math.min(Math.max((t-start)/dur,0),1),e=1-Math.pow(1-k,3);
        el.textContent=fmtMoney(from+(to-from)*e);
        if(k<1) requestAnimationFrame(step);
      })(start);
    }

    function milestoneHint(pct, raised, goal){
      const el=document.getElementById('fc-next'); if(!el) return;
      const steps=[25,50,75,100]; const next=steps.find(s=>pct < s);
      if(!next){ el.textContent='Thank you! Goal reached 🎉'; return; }
      const target = goal*(next/100), delta = Math.max(0, target - raised);
      el.textContent = `Only ${fmtMoney(delta)} to reach ${next}%`;
    }

    function setProgress(raised=state.raised,goal=state.goal){
      state.raised=+raised||0; state.goal=Math.max(+goal||1,1);
      const pct=Math.min(Math.max((state.raised/state.goal)*100,0),100);

      els.bar && (els.bar.style.width=pct.toFixed(1)+'%');
      els.pct && (els.pct.textContent=pct.toFixed(1));
      els.goal && (els.goal.textContent=fmtMoney(state.goal));
      els.raised && tweenNumber(els.raised,state.raised);
      els.progressWrap && els.progressWrap.setAttribute('aria-valuenow', pct.toFixed(1));
      milestoneHint(pct, state.raised, state.goal);

      [25,50,75,100].forEach(m=>{
        const ms=document.getElementById('fc-ms-'+m);
        const wrap=ms?.closest('.group'); wrap&&wrap.classList.toggle('active', pct>=m-0.01);
      });

      HEAT_ON && els.root && els.root.style.setProperty('--heat',(pct/100).toFixed(3));

      try{
        const key='fc_vip_hit',prev=parseFloat(sessionStorage.getItem(key)||'0');
        const crossed=[...VIPS].sort((a,b)=>a-b).find(th=>prev<th && state.raised>=th);
        if(crossed){sessionStorage.setItem(key,String(crossed)); burstConfetti(24+Math.min(48,crossed/250));}
      }catch{}

      try{ dispatchEvent(new CustomEvent('fc:funds:update',{detail:{raised:state.raised,goal:state.goal}})); }catch{}
    }

    function updateCountdown(){
      const now=new Date(), diff=Math.max(0,state.deadline-now), s=Math.floor(diff/1000);
      const d=Math.floor(s/86400), h=Math.floor((s%86400)/3600), m=Math.floor((s%3600)/60), sec=s%60;
      const c=els.countdown;
      c.days&&(c.days.textContent=String(d).padStart(2,'0'));
      c.hrs&&(c.hrs.textContent=String(h).padStart(2,'0'));
      c.min&&(c.min.textContent=String(m).padStart(2,'0'));
      c.sec&&(c.sec.textContent=String(sec).padStart(2,'0'));
    }

    function openCheckout(amount){
      const base='{{ donate_href }}';
      const url=base+(base.includes('?')?'&':'?')+'amount='+encodeURIComponent(amount||0);
      window.location.href=url;
    }

    document.querySelectorAll('#fc-hero .fc-cta').forEach(btn=>btn.addEventListener('click',()=>openCheckout(btn.dataset.amount)));
    document.getElementById('fc-donate')?.addEventListener('click',()=>openCheckout(0));

    (function share(){
      const btn=els.share, ok=els.shareOK, sr=document.getElementById('sr-live');
      if(!btn) return;
      btn.addEventListener('click', async (e)=>{
        e.preventDefault();
        const data={ title: document.title.replace(/ — .*/,''), text:'Back our team—every dollar helps!', url: location.href };
        try{ if(navigator.share){ await navigator.share(data); ok?.classList.remove('hidden'); setTimeout(()=>ok?.classList.add('hidden'), 1200); return; } }catch{}
        try{ await navigator.clipboard.writeText(data.url); sr && (sr.textContent='Link copied.'); ok?.classList.remove('hidden'); setTimeout(()=>ok?.classList.add('hidden'), 1200); }catch{}
      });
    })();

    (function abCopy(){try{
      const key='fc_ab_copy_hero_v1'; let v=localStorage.getItem(key);
      if(!v){ v=Math.random()<.5?'A':'B'; localStorage.setItem(key,v); }
      const AC={{ ab_copy|tojson|safe }}; const text=(v==='A'?AC[0]:(AC[1]||AC[0]));
      els.ab && (els.ab.textContent=text);
    }catch{}})();

    setProgress(state.raised,state.goal);
    updateCountdown(); setInterval(updateCountdown,1000);

    addEventListener('fc:funds:update',e=>{
      const d=e.detail||{};
      setProgress(typeof d.raised==='number'?d.raised:state.raised,
                  typeof d.goal==='number'?d.goal:state.goal);
      if(d.sponsorName && els.ticker){
        const safe=String(d.sponsorName).replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
        els.ticker.insertAdjacentHTML('beforeend', `<span class="mx-6 text-xs text-zinc-300">🏅 ${safe}</span>`);
      }
    },{passive:true});

    addEventListener('fc:meter:update',e=>{
      const d=e.detail||{}; window.updateHeroMeter(d.raised,d.goal);
    },{passive:true});

    // Public API
    window.updateHeroMeter = (raised,goal)=> setProgress(raised ?? state.raised, goal ?? state.goal);
    window.getHeroMeter    = ()=> ({ raised: state.raised, goal: state.goal });
  })();
  {% if script_close is defined %}{{ script_close() }}{% else %}</script>{% endif %}
</section>
"""

INDEX_CANDIDATES = ["app/templates/index.html", "app/templates/home.html"]
BASE_CANDIDATES  = ["app/templates/base.html", "app/templates/layout.html"]
HERO_PATH        = Path("app/templates/partials/hero_and_fundraiser.html")

def project_root() -> Path:
    p = Path.cwd()
    for cur in [p] + list(p.parents):
        if (cur / "app/templates/partials").exists():
            return cur
    return p

def backup(path: Path):
    if not path.exists(): return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    shutil.copy2(path, bak)
    print(f"• Backup → {bak}")

def write_hero(dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        txt = dest.read_text(encoding="utf-8")
        if SENTINEL in txt:
            print(f"✓ Hero already SV-elite: {dest}")
            return
        backup(dest)
    dest.write_text(HERO_SV_ELITE, encoding="utf-8")
    print(f"✓ Wrote SV-elite hero → {dest}")

def ensure_include(file: Path):
    if not file.exists(): return
    txt = file.read_text(encoding="utf-8")
    include_line = r'{% include "partials/hero_and_fundraiser.html" ignore missing with context %}'
    # If it already includes this partial, stop.
    if re.search(r'{%\s*include\s+"partials/hero_and_fundraiser\.html"', txt):
        return
    # Replace any older hero include variants
    patterns = [
        r'{%\s*include\s+"partials/hero_[^"]+\.html"[^%]*%}',
        r'{%\s*include\s+"partials/hero-and-fundraiser\.html"[^%]*%}',
        r'{%\s*include\s+"partials/hero\.html"[^%]*%}',
    ]
    changed = False
    for pat in patterns:
        if re.search(pat, txt):
            backup(file)
            txt = re.sub(pat, include_line, txt)
            file.write_text(txt, encoding="utf-8")
            print(f"✓ Rewired hero include in {file}")
            changed = True
            break
    if not changed:
        # Inject after header include or after <main> or at top
        hook = re.search(r'{%\s*include\s+"partials/header[^"]*"\s+[^%]*%}', txt)
        insert_at = hook.end() if hook else (re.search(r"<main[^>]*>", txt, re.I).end() if re.search(r"<main[^>]*>", txt, re.I) else 0)
        new_txt = txt[:insert_at] + ("\n" if insert_at else "") + include_line + "\n" + txt[insert_at:]
        backup(file)
        file.write_text(new_txt, encoding="utf-8")
        print(f"✓ Injected hero include into {file}")

def main():
    root = project_root()
    print(f"Root → {root}")
    write_hero(root / HERO_PATH)

    for rel in INDEX_CANDIDATES + BASE_CANDIDATES:
        f = root / rel
        if f.exists():
            ensure_include(f)

    print("✅ Done. Launch the app and verify the polished hero renders.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)

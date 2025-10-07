#!/usr/bin/env python3
"""
patch_hero.py  —  Auto-patch Flask/Jinja project with premium hero banner.

Usage:
  python patch_hero.py --project /path/to/app [--apply] [--no-csp] [--verbose]

What it does:
  - Writes/updates:
      static/css/hero.css
      static/js/hero.js
      templates/components/hero_banner.html
      templates/components/hero_banner_body.html
  - Patches templates/base.html to include hero.css/js
  - Adds filters + (optional) Flask-Talisman CSP in app.py
  - Adds a demo page templates/pages/home.html if missing
  - Creates .bak files before first write per target
"""

import argparse, os, re, sys, shutil
from pathlib import Path

MARK = "/* FUNDCHAMPS-HERO-AUTO */"
TEMPLATE_MARK = "{# FUNDCHAMPS-HERO-AUTO #}"

CSS = MARK + """
:root {
  --accent: #fbbf24;
  --bg: #0b0f19; --ink: #0b0f19; --ink-muted:#525f7a;
  --panel:#ffffff; --panel-ink:#0b0f19;
  --ring:2px solid #11182740; --radius:1.25rem; --shadow:0 10px 30px rgba(0,0,0,.15);
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#0a0a0a; --ink:#e8ecf1; --ink-muted:#a6b0bf; --panel:#111315; --panel-ink:#e8ecf1; --ring:2px solid #ffffff26; --shadow:0 10px 30px rgba(0,0,0,.5); }
}
*,*::before,*::after{ box-sizing:border-box; }
html{ -webkit-text-size-adjust:100%; }
body{ margin:0; font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial; color:var(--ink); background:var(--bg); line-height:1.45; }
img{ display:block; max-width:100%; height:auto; }
.sr-only{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }

/* Buttons */
.btn{ display:inline-flex; align-items:center; justify-content:center; gap:.5rem; padding:1rem 1.5rem; font-weight:700; border-radius:9999px; text-decoration:none; cursor:pointer; border:1px solid transparent; transition:transform .08s ease, background-color .2s ease, color .2s ease, border-color .2s ease; min-height:48px; min-width:44px; }
.btn:active{ transform:translateY(1px) scale(.99); }
.btn--gold{ background: var(--accent); color:#1f2937; border-color:#d97706; box-shadow: 0 10px 24px rgba(251,191,36,.25); }
.btn--gold:hover{ filter:brightness(.98); }
.btn--ghost{ background:transparent; color:var(--panel-ink); border-color:#d1d5db40; opacity:.95; }
.btn--ghost:hover{ background:#ffffff14; }
.btn--sm{ padding:.5rem .9rem; font-size:.9rem; min-height:40px; }
.pulse{ position:relative; }
.pulse::after{ content:""; position:absolute; inset:-4px; border-radius:inherit; border:2px solid var(--accent); opacity:.55; animation:pulse 1.9s ease-out infinite; }
@media (prefers-reduced-motion: reduce){ .pulse::after{ animation:none; } }
@keyframes pulse{ 0%{ transform:scale(.98); opacity:.8 } 100%{ transform:scale(1.2); opacity:0 } }

/* Hero layout */
.hero{ --gap: clamp(1rem, 2vw, 2rem); padding: max(1rem, env(safe-area-inset-top)) 1rem 1.25rem; }
.hero__inner{ max-width:1200px; margin-inline:auto; }
.hero__grid{ display:grid; gap: var(--gap); grid-template-columns: 1fr; }
@media (min-width: 960px){ .hero__grid{ grid-template-columns: 1.2fr .8fr; align-items:stretch; } }

/* Media + overlay */
.hero__left{ position:relative; }
.hero__media{ position:relative; border-radius: var(--radius); overflow:hidden; box-shadow: var(--shadow); background:#0b0f19; }
.hero__img{ width:100%; aspect-ratio: 16/10; object-fit: cover; filter: saturate(1.05) contrast(1.05); }
.hero__media::before{ content:""; position:absolute; inset:0;
  background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,.25) 38%, rgba(0,0,0,.70) 100%),
              radial-gradient(60% 50% at 50% 65%, rgba(0,0,0,.35), rgba(0,0,0,0) 70%);
  pointer-events:none; }
.hero__overlay{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding: clamp(1rem, 4vw, 3rem); color:#fff; gap:1rem; max-width:64rem; margin-inline:auto; }
.hero__overlay .chip{ background:#ffffff24; color:#fff; border:1px solid #ffffff3d; padding:.4rem .75rem; border-radius:9999px; font-weight:700; letter-spacing:.02em; }
.tagline{ margin:0; font-weight:900; line-height:1.05; font-size: clamp(2rem, 6vw, 3.5rem); }
.tagline .accent{ color: var(--accent); text-shadow: 0 1px 0 #0006; }
.sub{ margin:0; font-size: clamp(1rem, 3.2vw, 1.125rem); color:#e6edf6; max-width: 60ch; }

/* KPI chips */
.kpis{ display:flex; gap:.75rem; flex-wrap:wrap; justify-content:center; margin:.25rem 0 0; padding:0; list-style:none; }
.kpis li{ background:#111827aa; color:#f3f4f6; border:1px solid #ffffff1f; padding:.55rem .8rem; border-radius:9999px; display:flex; align-items:center; gap:.5rem; }
.kpi-val{ font-size:1.05rem; } .kpi-label{ font-size:.95rem; opacity:.95; }

/* Trust + QR */
.hero-trust{ display:flex; gap:.75rem; flex-wrap:wrap; justify-content:center; align-items:center; color:#e5e7eb; }
.tax-badge,.secure-badge{ font-size:.85rem; background:#111827aa; border:1px solid #ffffff24; padding:.35rem .7rem; border-radius:9999px; }
.qr-hero{ display:flex; gap:.75rem; align-items:center; justify-content:center; }
.qr-hero img{ border-radius:.75rem; border:1px solid #ffffff24; }
.qr-hero .qr-cap{ font-size:.95rem; color:#f3f4f6; }

/* CTA row */
.cta{ display:flex; gap:.75rem; flex-wrap:wrap; justify-content:center; }

/* Scoreboard */
.scoreboard{ background: linear-gradient(180deg, #0f1422, #0c111b); color: var(--panel-ink); border-radius: var(--radius); box-shadow: var(--shadow); border:1px solid #ffffff12; margin-top: -2.25rem; }
@media (max-width:640px){ .scoreboard{ margin-top:-1.5rem; } }
.panel__inner{ padding: clamp(1rem, 2.5vw, 2rem); display:flex; flex-direction:column; gap:1.1rem; }
.brand .chip--sm{ font-size:.8rem; background:#eef2ff; color:#111827; border:1px solid #c7d2fe; }
.title{ margin:0; font-size: clamp(1.3rem, 4.2vw, 2rem); line-height:1.15; } .title .accent{ color: var(--accent); }
.scan-hint{ font-size:.9rem; color: var(--ink-muted); }

.score .money{ font-variant-numeric: tabular-nums lining-nums; font-size: clamp(1.3rem, 6vw, 2.2rem); display:flex; align-items:baseline; gap:.35rem; font-weight:800; letter-spacing:.2px; }
.score .pct{ font-weight:700; color: var(--accent); }
.timer{ display:flex; justify-content:space-between; align-items:center; background:#0f172a; color:#e5e7eb; border:1px solid #ffffff10; border-radius:.75rem; padding:.5rem .75rem; font-size:.95rem; }

.meter-wrap{ display:grid; gap:.5rem; }
.meter{ width:100%; height:12px; } .track{ position:relative; height:14px; background:#ffffff12; border-radius:9999px; overflow:hidden; }
.fill{ position:absolute; inset:0 auto 0 0; width: var(--p, 0%); background: linear-gradient(90deg, var(--accent), color-mix(in oklab, var(--accent), white 15%)); border-radius: inherit; transition: width .6s ease; box-shadow: inset 0 -1px 0 rgba(0,0,0,.2); }

.chips{ display:flex; gap:.5rem; flex-wrap:wrap; }
.chip-btn{ border-radius:9999px; border:1px solid #d1d5db; background:#fff; color:#111827; padding:.8rem 1rem; font-weight:700; cursor:pointer; }
.chip-btn[aria-pressed="true"]{ background: color-mix(in srgb, var(--accent), white 85%); border-color: var(--accent); }
@media (prefers-color-scheme: dark){ .chip-btn{ background:#0f172a; color:#e5e7eb; border-color:#334155; } }

.sticky{ position:sticky; bottom:0; background: linear-gradient(180deg, #0000, #0000 20%, color-mix(in srgb, #0c111b, white 4%)); padding-top:.25rem; }
.toggle{ display:inline-flex; align-items:center; gap:.5rem; margin-left:.5rem; font-size:.95rem; }

/* Ticker (if present) */
.lb__rail{ display:flex; gap:2rem; animation: ticker 42s linear infinite; }
@keyframes ticker{ from{ transform:translateX(100%);} to{ transform:translateX(-100%);} }
.lb__rail .pill .txt{ font-size:1.05rem; line-height:1.5; }
@media (max-width: 480px){ .lb__rail .pill{ padding:.8rem 1rem; } }
@media (prefers-reduced-motion: reduce){ .lb__rail{ animation:none; } }

/* Mobile refinements */
h1,h2,.tagline{ font-size: clamp(2rem, 6vw, 3.2rem); }
.sub,.kpi-label{ font-size: clamp(1rem, 3vw, 1.125rem); }
.donation-amount{ font-size: clamp(2rem, 5vw, 3rem); font-weight:800; color: var(--accent); }
@media (max-width:768px){ .btn{ padding:1.2rem 1.6rem; font-size:1.05rem; } .nav a{ padding:.8rem 1.2rem; font-size:1.1rem; } }
"""

JS = MARK + """
// Attach behavior to the closest .hero section
const el = document.querySelector('.hero'); if (!el) return;
const id = el.id || 'hero';
const currency = el.dataset.currency || 'USD';
const raised = Number(el.dataset.raised || 0);
const goal = Math.max(1, Number(el.dataset.goal || 1));
const deadlineIso = el.dataset.deadline || '';
const fmt = new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 0 });

const moneyWrap = el.querySelector('.money');
const raisedEl = el.querySelector('[data-role="raised"]');
const goalEl = el.querySelector('[data-role="goal"]');
const pctEl = el.querySelector('[data-role="pct"]');
const meterFill = el.querySelector('.fill');
const meter = el.querySelector('meter');
const deadlineEl = el.querySelector(`#${CSS.escape(id)}-deadline`);
const chips = [...el.querySelectorAll('.chip-btn')];
const donateBtn = el.querySelector(`#${CSS.escape(id)}-donate`);
const donateAmtSpan = donateBtn?.querySelector('.amt');
const monthlyToggle = el.querySelector(`#${CSS.escape(id)}-monthly`);
const shareBtn = el.querySelector(`#${CSS.escape(id)}-share`);
const shareLive = el.querySelector(`#${CSS.escape(id)}-share-live`);

// Values
const pct = Math.min(100, Math.round((raised / goal) * 100));
if (raisedEl) raisedEl.textContent = fmt.format(raised);
if (goalEl) goalEl.textContent = fmt.format(goal);
if (pctEl) pctEl.textContent = `• ${pct}%`;
if (meter) meter.value = raised;
if (meterFill) meterFill.style.setProperty('--p', `${pct}%`);

// Countdown (low CPU)
function tickCountdown(){
  if (!deadlineIso || !deadlineEl) return;
  const end = new Date(deadlineIso); const now = new Date(); const diff = end - now;
  if (Number.isNaN(end.getTime()) || diff <= 0){ deadlineEl.textContent = 'Ends soon'; return; }
  const d = Math.floor(diff / (1000*60*60*24));
  const h = Math.floor((diff / (1000*60*60)) % 24);
  const m = Math.floor((diff / (1000*60)) % 60);
  deadlineEl.textContent = `${d}d ${h}h ${m}m`;
}
tickCountdown(); const timerId = window.setInterval(tickCountdown, 30_000);
window.addEventListener('visibilitychange', () => { if (document.hidden) window.clearInterval(timerId); });

// Quick amount chips + monthly toggle
const storeKey = `donate:${id}`;
function setActiveChip(btn){
  chips.forEach(b => b.setAttribute('aria-pressed', String(b===btn)));
  const amt = Number(btn?.dataset.amt||0);
  const url = new URL(donateBtn.href, location.origin);
  if (amt) url.searchParams.set('amount', String(amt));
  if (monthlyToggle?.checked) url.searchParams.set('interval', 'month'); else url.searchParams.delete('interval');
  donateBtn.href = url.toString();
  if (donateAmtSpan) donateAmtSpan.textContent = amt ? fmt.format(amt) : '';
  localStorage.setItem(storeKey, JSON.stringify({amt, monthly: !!monthlyToggle?.checked}));
}
chips.forEach(b => b.addEventListener('click', () => setActiveChip(b)));
monthlyToggle?.addEventListener('change', () => {
  const active = chips.find(b => b.getAttribute('aria-pressed') === 'true');
  if (active) setActiveChip(active); else {
    const url = new URL(donateBtn.href, location.origin);
    if (monthlyToggle.checked) url.searchParams.set('interval', 'month'); else url.searchParams.delete('interval');
    donateBtn.href = url.toString();
    const state = JSON.parse(localStorage.getItem(storeKey)||'{}');
    localStorage.setItem(storeKey, JSON.stringify({ ...state, monthly: !!monthlyToggle.checked }));
  }
});
// Restore
try{ const state = JSON.parse(localStorage.getItem(storeKey)||'null');
  if (state?.amt){ const match = chips.find(b=>Number(b.dataset.amt)===Number(state.amt)); if (match) setActiveChip(match); }
  if (monthlyToggle && typeof state?.monthly === 'boolean') monthlyToggle.checked = state.monthly;
}catch{}

// Hotkey D to donate (disabled while typing)
function isTyping(){ const a = document.activeElement; return a && (a.tagName==='INPUT' || a.tagName==='TEXTAREA' || a.isContentEditable); }
window.addEventListener('keydown', (e)=>{ if ((e.key==='d'||e.key==='D') && !isTyping()) donateBtn?.click(); });

// Share
shareBtn?.addEventListener('click', async ()=>{
  const title = document.title || 'Support our team'; const url = location.href;
  shareBtn.setAttribute('aria-expanded', 'true');
  try{ if (navigator.share){ await navigator.share({ title, url }); shareLive.textContent = 'Share sheet opened.'; }
       else{ await navigator.clipboard.writeText(url); shareLive.textContent = 'Link copied to clipboard.'; } }
  catch{ shareLive.textContent = 'Share canceled.'; }
  window.setTimeout(()=>{ shareLive.textContent=''; shareBtn.setAttribute('aria-expanded','false'); }, 3000);
});

// Ticker pause/resume if ticker exists
const rail = document.querySelector('.lb__rail');
const pauseBtn = document.querySelector('[data-act="pause"]');
const setPaused = (p)=>{ if (rail) rail.style.animationPlayState = p?'paused':'running'; pauseBtn?.setAttribute('aria-pressed', String(p)); };
pauseBtn?.addEventListener('click', ()=> setPaused(pauseBtn.getAttribute('aria-pressed')!=='true'));
if (rail) new IntersectionObserver(([entry])=> setPaused(!entry.isIntersecting), {threshold:.01}).observe(rail);

// Analytics hook
document.querySelectorAll('[data-cta]')?.forEach(el=>{
  el.addEventListener('click', ()=> window.dispatchEvent(new CustomEvent('cta:click', { detail: { cta: el.getAttribute('data-cta'), id, href: el.href }})));
});
"""

MACRO = TEMPLATE_MARK + """
{% macro hero_banner(
  idp,
  theme_hex,
  team_name,
  title,
  title_2,
  subtitle,
  panel_title,
  panel_title_2,
  href_donate,
  href_impact,
  href_sponsor,
  text_keyword,
  text_short,
  raised,
  goal,
  deadline='',
  currency='USD',
  hero_src='',
  hero_src_avif='',
  hero_src_webp='',
  hero_src_800='',
  hero_src_1200='',
  hero_src_1600='',
  hero_src_2000='',
  qr_src=''
) %}
<section
  id="{{ idp }}"
  class="hero"
  style="--accent: {{ theme_hex }};"
  aria-label="Fundraiser hero and live scoreboard"
  data-raised="{{ raised }}"
  data-goal="{{ goal }}"
  data-deadline="{{ deadline }}"
  data-currency="{{ currency }}"
>
  {% include 'components/hero_banner_body.html' %}
</section>
{% endmacro %}
"""

BODY = TEMPLATE_MARK + """
<header class="hero__left" role="region" aria-labelledby="{{ idp }}-headline">
  <figure class="hero__media">
    <picture>
      {% if hero_src_avif %}<source type="image/avif" srcset="{{ hero_src_avif }}">{% endif %}
      {% if hero_src_webp %}<source type="image/webp" srcset="{{ hero_src_webp }}">{% endif %}
      <img src="{{ hero_src }}" alt="{{ team_name }} team photo" class="hero__img" decoding="async" fetchpriority="high"
           sizes="(max-width: 950px) 100vw, 60vw"
           srcset="{% if hero_src_800 %}{{ hero_src_800 }} 800w,{% endif %}
                   {% if hero_src_1200 %}{{ hero_src_1200 }} 1200w,{% endif %}
                   {% if hero_src_1600 %}{{ hero_src_1600 }} 1600w,{% endif %}
                   {% if hero_src_2000 %}{{ hero_src_2000 }} 2000w{% endif %}">
    </picture>

    <figcaption class="hero__overlay hero__overlay--centered">
      <span class="chip" id="{{ idp }}-headline">{{ team_name }}</span>
      <h1 class="tagline"><span>{{ title }}</span> <span class="accent">{{ title_2 }}</span></h1>
      <p class="sub" id="{{ idp }}-deck">{{ subtitle }}</p>

      <ul class="kpis" aria-label="Team stats">
        <li><span class="kpi-val"><b>35+</b></span><span class="kpi-label">Games Played</span></li>
        <li><span class="kpi-val"><b>5</b></span><span class="kpi-label">Championships</span></li>
        <li><span class="kpi-val"><b>120+</b></span><span class="kpi-label">Training Hours / Week</span></li>
      </ul>

      <nav class="cta" aria-label="Hero Actions">
        <a href="{{ href_impact }}" class="btn btn--ghost" data-cta="impact">🏀 Back Our Ballers</a>
        <a href="{{ href_donate }}" id="{{ idp }}-donate" class="btn btn--gold pulse" data-cta="donate" target="_blank" rel="noopener noreferrer" aria-label="Donate to {{ team_name }}">
          ⛹️ Fuel the Season <span class="amt" aria-hidden="true"></span>
        </a>
      </nav>

      <div class="hero-trust">
        <span class="tax-badge">100% TAX DEDUCTIBLE</span>
        <span class="secure-badge">SECURE VIA STRIPE / PAYPAL</span>
      </div>

      <div class="qr-hero">
        <img id="{{ idp }}-qr" src="{{ qr_src }}" alt="QR code to donate to {{ team_name }}" width="98" height="98" decoding="async" loading="lazy" />
        <div class="qr-cap"><b>Scan to give</b> — or press <kbd>D</kbd></div>
      </div>
    </figcaption>
  </figure>
</header>

<aside class="scoreboard" aria-labelledby="{{ idp }}-panel-title" role="complementary">
  <div class="panel__inner">
    <div class="brand"><span class="chip chip--sm">{{ team_name }}</span></div>
    <h2 id="{{ idp }}-panel-title" class="title"><span>{{ panel_title }}</span> <span class="accent">{{ panel_title_2 }}</span></h2>
    <p class="sub">Direct support for gear, travel, coaching, and tutoring—every dollar moves a kid forward.</p>
    <p class="scan-hint" aria-hidden="true">Scan to give — or press <kbd>D</kbd></p>

    <section class="score" aria-label="Fundraising progress">
      <div class="money tabular" aria-live="polite">
        <span class="raised" data-role="raised">{{ raised|roll_money(currency) }}</span>
        <span class="sep" aria-hidden="true">/</span>
        <span class="goal" data-role="goal">{{ goal|roll_money(currency) }}</span>
        <span class="pct" data-role="pct">• {{ ((raised/goal)*100)|clamp_pct|roll_pct }}%</span>
      </div>
      <div class="timer"><span class="label">Goal ends in</span><time id="{{ idp }}-deadline" class="value" data-deadline="{{ deadline }}" aria-live="polite">—</time></div>
    </section>

    <div class="meter-wrap">
      <meter class="meter" min="0" max="{{ goal|int }}" value="{{ raised|int }}" aria-describedby="{{ idp }}-panel-title">{{ ((raised/goal)*100)|clamp_pct|roll_pct }}% of goal</meter>
      <div class="track" aria-hidden="true"><div class="fill" style="--p: {{ ((raised/goal)*100)|clamp_pct }}%"></div></div>
    </div>

    <div class="chips" role="group" aria-label="Quick donation amounts">
      <button class="chip-btn" type="button" data-amt="25" aria-pressed="false">+$25 <em>· 1 team meal</em></button>
      <button class="chip-btn" type="button" data-amt="50" aria-pressed="false">+$50 <em>· 1 jersey piece</em></button>
      <button class="chip-btn" type="button" data-amt="100" aria-pressed="false">+$100 <em>· 1 week of gym time</em></button>
    </div>

    <div class="sticky">
      <div class="cta">
        <a id="{{ idp }}-donate" class="btn btn--gold" href="{{ href_donate }}" target="_blank" rel="noopener noreferrer" data-cta="donate">Donate <span class="amt" aria-hidden="true"></span> →</a>
        <label class="toggle"><input id="{{ idp }}-monthly" name="monthly" type="checkbox" /><span>Make it monthly</span></label>
      </div>
      <span id="{{ idp }}-donate-kbd" class="sr-only">Tip: Press D to donate. Hotkey is disabled while typing.</span>
      <p class="note">Every <b>$100</b> ≈ a week of gym time.</p>
    </div>

    <nav class="sec" aria-label="Secondary actions">
      <a class="btn btn--ghost btn--sm" href="{{ href_donate }}" target="_blank" rel="noopener noreferrer">Skip to Donate</a>
      <a class="btn btn--ghost btn--sm" href="{{ href_impact }}">Impact</a>
      <a class="btn btn--ghost btn--sm" href="{{ href_sponsor }}">Become a Sponsor</a>
      <button class="btn btn--ghost btn--sm" type="button" id="{{ idp }}-share" aria-controls="{{ idp }}-share-live" aria-expanded="false">Share</button>
      <span id="{{ idp }}-share-live" class="sr-only" aria-live="polite"></span>
    </nav>

    <div class="ladder" role="group" aria-label="Impact ladder milestones">
      <div class="rung" data-threshold="1000"><div class="bar"></div><div class="lbl"><span class="amt">$1,000</span><span class="what">Gym Week</span></div></div>
      <div class="rung" data-threshold="5000"><div class="bar"></div><div class="lbl"><span class="amt">$5,000</span><span class="what">Travel Slot</span></div></div>
      <div class="rung" data-threshold="10000"><div class="bar"></div><div class="lbl"><span class="amt">$10,000</span><span class="what">Tutor Block</span></div></div>
    </div>

    <p class="sms">📱 Text <b>{{ text_keyword }}</b> to <b>{{ text_short }}</b> to give.</p>
  </div>
</aside>
"""

BASE_PATCH = TEMPLATE_MARK + """
  <link rel="preload" href="{{ url_for('static', filename='css/hero.css', v='1.0.0') }}" as="style">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/hero.css', v='1.0.0') }}">
  <!-- {# FUNDCHAMPS-HERO-AUTO #} CSS END -->
"""

BASE_JS = TEMPLATE_MARK + """
  <script type="module" src="{{ url_for('static', filename='js/hero.js', v='1.0.0') }}"></script>
  <!-- {# FUNDCHAMPS-HERO-AUTO #} JS END -->
"""

HOME = TEMPLATE_MARK + """
{% extends "base.html" %}
{% from "components/hero_banner.html" import hero_banner %}

{% block title %}Home – {{ team_name }}{% endblock %}

{% block content %}
  {{ hero_banner(
    idp='hero-1',
    theme_hex=theme_hex,
    team_name=team_name,
    title=title,
    title_2=title_2,
    subtitle=subtitle,
    panel_title=panel_title,
    panel_title_2=panel_title_2,
    href_donate=href_donate,
    href_impact=href_impact,
    href_sponsor=href_sponsor,
    text_keyword=text_keyword,
    text_short=text_short,
    raised=raised,
    goal=goal,
    deadline=deadline,
    currency=currency,
    hero_src=url_for('static', filename='img/team-hero.jpg'),
    qr_src=url_for('static', filename='img/qr.png')
  ) }}
{% endblock %}
"""

APP = """# FUNDCHAMPS-HERO-AUTO
from flask import Flask, render_template
try:
    from babel.numbers import format_currency
    HAVE_BABEL = True
except Exception:
    HAVE_BABEL = False

app = Flask(__name__)

# --- Filters ---
@app.template_filter("roll_money")
def roll_money(amount, currency="USD"):
    try:
        if HAVE_BABEL:
            return format_currency(amount, currency, locale="en_US")
        return f"${int(float(amount)):,}"
    except Exception:
        return f"${int(amount):,}"

@app.template_filter("roll_pct")
def roll_pct(pct):
    try:
        return int(round(float(pct)))
    except Exception:
        return 0

@app.template_filter("clamp_pct")
def clamp_pct(value):
    try:
        v = float(value)
        return 0 if v < 0 else 100 if v > 100 else int(round(v))
    except Exception:
        return 0

@app.route("/")
def home():
    data = dict(
        theme_hex="#fbbf24", team_name="Connect ATX Elite",
        title="Fuel the Season.", title_2="Fund the Future.",
        subtitle="Every dollar powers our journey: gear, travel, coaching, and tutoring.",
        panel_title="Live", panel_title_2="Scoreboard",
        href_donate="https://example.com/donate", href_impact="/impact", href_sponsor="/sponsor",
        text_keyword="ELITE", text_short="444321",
        raised=0, goal=50000, deadline="", currency="USD"
    )
    return render_template("pages/home.html", **data)

if __name__ == "__main__":
    app.run(debug=True)
"""

CSP_SNIPPET = """
# FUNDCHAMPS-HERO-AUTO-CSP
try:
    from flask_talisman import Talisman
    csp = {
      'default-src': "'self'",
      'img-src': "'self' data:",
      'style-src': "'self'",
      'script-src': "'self'",
      'connect-src': "'self'",
    }
    Talisman(app, content_security_policy=csp, force_https=True)
except Exception:
    pass
"""

def write_if_changed(path: Path, content: str, apply: bool, verbose: bool):
    if path.exists():
        existing = path.read_text(encoding="utf-8", errors="ignore")
        if existing == content:
            if verbose: print(f"= OK (unchanged): {path}")
            return False
        # first-time backup
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists() and apply:
            shutil.copy2(path, bak)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    if apply:
        path.write_text(content, encoding="utf-8")
        print(f"+ Wrote: {path}")
    else:
        print(f"~ Would write: {path}")
    return True

def insert_once(file: Path, needle: str, block: str, where="after", apply=False, verbose=False):
    if not file.exists():
        print(f"! Skipping patch (missing): {file}")
        return False
    txt = file.read_text(encoding="utf-8", errors="ignore")
    if TEMPLATE_MARK in txt or MARK in txt:
        if verbose: print(f"= Already contains patch markers: {file}")
        return False
    # insert before </head> or before </body> depending on block
    if "CSS END" in block:
        pat = re.compile(r"</head>", re.I)
        repl = block + "\n</head>"
    else:
        pat = re.compile(r"</body>", re.I)
        repl = block + "\n</body>"
    if not pat.search(txt):
        print(f"! Could not find insertion point in {file.name}; skipping.")
        return False
    new = pat.sub(repl, txt, count=1)
    if apply:
        bak = file.with_suffix(file.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(file, bak)
        file.write_text(new, encoding="utf-8")
        print(f"* Patched: {file}")
    else:
        print(f"~ Would patch: {file}")
    return True

def ensure_app_py(app_py: Path, add_csp: bool, apply: bool, verbose: bool):
    if not app_py.exists():
        return write_if_changed(app_py, APP + (CSP_SNIPPET if add_csp else ""), apply, verbose)
    txt = app_py.read_text(encoding="utf-8", errors="ignore")
    changed = False
    if "roll_money" not in txt:
        txt += "\n\n" + APP.split("# --- Filters ---",1)[1]  # append filters + route
        changed = True
    if add_csp and "FUNDCHAMPS-HERO-AUTO-CSP" not in txt:
        txt += "\n" + CSP_SNIPPET
        changed = True
    if changed:
        if apply:
            bak = app_py.with_suffix(".py.bak")
            if not bak.exists():
                shutil.copy2(app_py, bak)
            app_py.write_text(txt, encoding="utf-8")
            print(f"* Updated: {app_py}")
        else:
            print(f"~ Would update: {app_py}")
    else:
        if verbose: print(f"= app.py already has filters/CSP/route")
    return changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Path to Flask project root")
    ap.add_argument("--apply", action="store_true", help="Write changes to disk")
    ap.add_argument("--no-csp", action="store_true", help="Skip Flask-Talisman CSP patch")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    static = root / "static"
    templates = root / "templates"
    components = templates / "components"
    pages = templates / "pages"
    base_html = templates / "base.html"
    app_py = root / "app.py"

    # 1) Assets
    write_if_changed(static / "css" / "hero.css", CSS, args.apply, args.verbose)
    write_if_changed(static / "js" / "hero.js", JS, args.apply, args.verbose)

    # 2) Templates
    write_if_changed(components / "hero_banner.html", MACRO, args.apply, args.verbose)
    write_if_changed(components / "hero_banner_body.html", BODY, args.apply, args.verbose)

    # 3) base.html patches
    if base_html.exists():
        insert_once(base_html, "</head>", BASE_PATCH, apply=args.apply, verbose=args.verbose)
        insert_once(base_html, "</body>", BASE_JS, apply=args.apply, verbose=args.verbose)
    else:
        # create a minimal base.html if missing
        base_min = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{% block title %}Fundraiser{% endblock %}</title>
""" + BASE_PATCH + """
</head><body>
{% block content %}{% endblock %}
""" + BASE_JS + """
</body></html>"""
        write_if_changed(base_html, base_min, args.apply, args.verbose)

    # 4) Demo page if missing
    if not (pages / "home.html").exists():
        write_if_changed(pages / "home.html", HOME, args.apply, args.verbose)

    # 5) app.py filters + optional CSP
    ensure_app_py(app_py, add_csp=(not args.no_csp), apply=args.apply, verbose=args.verbose)

    print("\nDone. Run your app and visit '/'. Re-run with --apply after a dry run if needed.")

if __name__ == "__main__":
    main()


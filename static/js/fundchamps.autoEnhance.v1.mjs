/* FundChamps Auto-Enhance v1.0 (ESM, CSP-safe, no-deps)
   - Perf: lazy-img pass, preconnect Stripe, rAF batching
   - A11y: labels, roles, aria-fixes, focus guards, external noopener
   - UX: hotkeys (D/S/M), sticky donate, Web Share fallback
   - Biz: UTM/src stitching for donate+sponsor links
   - Reports: window.FundChampsReport + console table
*/

const CFG = Object.assign({
  donateSelector: "[data-donate-cta], a[href*='/donate']",
  sponsorSelector: "a[data-tier], a[href*='/sponsor']",
  headerSelector: "#site-header",
  sentinelSelector: "#site-header-sentinel",
  floatingCtaSelector: "#floating-donate-cta",
  stickyDonateMinWidth: 861,         // float CTA visible below this width only
  enrichUTM: true,
  addLazyToImages: true,
  enforceNoopener: true,
  ariaAutofix: true,
  hotkeys: true,
  reportToWindow: true
}, (globalThis.FC_ENHANCE_CFG || {}));

const q  = (s, r=document) => r.querySelector(s);
const qq = (s, r=document) => Array.from(r.querySelectorAll(s));
const on = (el, ev, fn, opt) => el && el.addEventListener(ev, fn, opt);
const raf = (fn) => requestAnimationFrame(fn);
const prefersReducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const prefersReducedData   = matchMedia('(prefers-reduced-data: reduce)').matches;

const report = {
  timestamp: new Date().toISOString(),
  fixes: [],
  warnings: [],
  info: []
};
function logFix(kind, detail){ report.fixes.push({kind, detail}); }
function warn(msg, meta){ report.warnings.push({msg, meta}); }
function info(msg, meta){ report.info.push({msg, meta}); }

function fmtMoney(n){ return '$'+Number(n||0).toLocaleString('en-US',{maximumFractionDigits:0}); }

// -------------------------
// 0) Safe utilities
// -------------------------
function setNoopenerForExternalTargets(root=document){
  if(!CFG.enforceNoopener) return;
  qq('a[target="_blank"]', root).forEach(a=>{
    const rel = (a.getAttribute('rel')||'').toLowerCase();
    if(!/\bnoopener\b/.test(rel)){
      a.setAttribute('rel', (rel ? rel+' ' : '') + 'noopener');
      logFix('rel_noopener', a.outerHTML.slice(0,160));
    }
  });
}

function addLazyToImages(root=document){
  if(!CFG.addLazyToImages) return;
  qq('img:not([loading]), img[loading="eager"]', root).forEach(img=>{
    // Don’t touch likely LCP if fetchpriority=high
    if(img.getAttribute('fetchpriority') === 'high') return;
    img.setAttribute('loading','lazy');
    logFix('img_lazy', img.src || img.getAttribute('srcset') || img.outerHTML.slice(0,140));
  });
}

function stripePreconnect(){
  // harmless if unused
  const link = document.createElement('link');
  link.rel = 'preconnect';
  link.href = 'https://js.stripe.com';
  link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
  info('preconnect_stripe');
}

function inView(el){
  const r = el.getBoundingClientRect();
  return r.top < innerHeight && r.bottom > 0 && r.right > 0 && r.left < innerWidth;
}

// -------------------------
// 1) Sticky header polish
// -------------------------
function initStickyHeader(){
  const hdr = q(CFG.headerSelector);
  const snt = q(CFG.sentinelSelector);
  if(!hdr || !snt || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((entries)=>{
    const e = entries[0];
    hdr.classList.toggle('is-stuck', e.intersectionRatio < 1 && e.boundingClientRect.top < 0);
  }, { threshold: [1] });
  io.observe(snt);
  info('sticky_header_initialized');
}

// -------------------------
// 2) Floating donate CTA
// -------------------------
function initFloatingDonate(){
  const float = q(CFG.floatingCtaSelector);
  if(!float) return;

  const scan = () => {
    if(innerWidth >= CFG.stickyDonateMinWidth){
      float.style.display = 'none';
      return;
    }
    const donateBtns = qq(CFG.donateSelector);
    let visible = false;
    for(const b of donateBtns){ if(inView(b)){ visible = true; break; } }
    float.style.display = visible ? 'none' : 'grid';
  };
  on(window, 'scroll', ()=>raf(scan), { passive:true });
  on(window, 'resize', scan);
  scan();
  info('floating_donate_initialized', { minWidth: CFG.stickyDonateMinWidth });
}

// -------------------------
// 3) Hotkeys (D/S/M)
// -------------------------
function initHotkeys(){
  if(!CFG.hotkeys) return;
  const isTyping = (e) => {
    const t = e.target;
    return t && (t.isContentEditable || /^(input|textarea|select)$/i.test(t.tagName));
  };
  on(document, 'keydown', (e)=>{
    if(isTyping(e) || e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key?.toLowerCase();
    if(k === 'd'){
      (q(CFG.donateSelector) || q('#hdr-donate'))?.focus();
    } else if(k === 's'){
      q('#hdr-share')?.click();
    } else if(k === 'm'){
      q('[data-monthly]')?.click();
    }
  }, { passive:true });
  info('hotkeys_enabled', { keys: 'D,S,M' });
}

// -------------------------
// 4) Share fallback
// -------------------------
function initShare(){
  const el = q('#hdr-share');
  if(!el) return;
  on(el, 'click', async ()=>{
    const data = JSON.parse(el.getAttribute('data-share')||'{}');
    try{
      if(navigator.share && !prefersReducedData){ await navigator.share(data); }
      else{
        await navigator.clipboard.writeText(data.url || location.href);
        const prev = el.textContent; el.textContent = 'Copied';
        setTimeout(()=> el.textContent = prev, 1200);
      }
      info('share_clicked');
    }catch(_){}
  }, { passive:true });
}

// -------------------------
// 5) Donate URL builder + chips + monthly
// -------------------------
function initDonateRuntime(){
  const aside = q('.fcx-scoreboard');
  const donateCTA = q('[data-donate-cta]');
  if(!aside || !donateCTA) return;

  const GOAL   = Number(aside.dataset.goal || '0');
  let   RAISED = Number(aside.dataset.raised || '0');
  const BASE   = aside.dataset.donateUrl || donateCTA.getAttribute('href') || '/donate';
  const TEAM   = aside.dataset.team || '';
  const CAMPA  = aside.dataset.campaign || '';

  const chipsWrap  = q('.fcx-chips');
  const monthlyChk = q('[data-monthly]');
  const raisedEl   = q('.fcx-raised');
  const meterFill  = q('.fcx-track .fcx-fill');
  const meterDom   = q('meter.fcx-meter');
  const sticky     = q('#sticky-progress');

  let selected = null;
  let monthly = false;

  function buildUrl(){
    const u = new URL(BASE, location.origin);
    if(CAMPA) u.searchParams.set('campaign', CAMPA);
    if(TEAM)  u.searchParams.set('team', TEAM);
    if(selected) u.searchParams.set('amount', String(selected));
    if(monthly)  u.searchParams.set('interval', 'month');
    return u.toString();
  }
  function updateCTA(){
    donateCTA.setAttribute('href', buildUrl());
    const amt = donateCTA.querySelector('.fcx-amt');
    if(amt) amt.textContent = selected ? ` ${fmtMoney(selected)}` : '';
  }
  function pct(){
    const p = GOAL > 0 ? Math.min(100, Math.max(0, (RAISED/GOAL)*100)) : 0;
    return Math.round(p);
  }
  function updateMeter(){
    const p = pct();
    if(meterDom) meterDom.value = RAISED;
    raf(()=>{ if(meterFill) meterFill.style.width = p + '%'; if(sticky) sticky.style.width = p + '%'; });
  }

  if(chipsWrap){
    on(chipsWrap, 'click', e=>{
      const b = e.target.closest('.fcx-chip-btn');
      if(!b) return;
      selected = Number(b.dataset.amt || '0');
      qq('.fcx-chip-btn', chipsWrap).forEach(x=>x.setAttribute('aria-pressed', x===b ? 'true':'false'));
      updateCTA();
      info('amount_selected', { amount: selected });
    });
  }
  if(monthlyChk){
    on(monthlyChk, 'change', ()=>{
      monthly = !!monthlyChk.checked;
      updateCTA();
      info('monthly_toggled', { monthly });
    });
  }

  // expose live updater
  globalThis.fcScoreboard = {
    add: (amount=0)=>{ RAISED = Math.max(0, RAISED + Number(amount||0)); if(raisedEl) raisedEl.textContent = fmtMoney(RAISED); updateMeter(); },
    set: (amount=0)=>{ RAISED = Math.max(0, Number(amount||0)); if(raisedEl) raisedEl.textContent = fmtMoney(RAISED); updateMeter(); }
  };

  updateCTA(); updateMeter();
}

// -------------------------
// 6) Tiers: filters & compare popovers
// -------------------------
function initTiers(){
  const root = q('#tiers');
  if(!root) return;
  const grid = root.querySelector('.grid, #tiers-grid') || root;
  const filters = root.querySelector('.filters');

  on(filters, 'click', (e)=>{
    const btn = e.target.closest('.chip.ctrl');
    if(!btn) return;
    const val = btn.dataset.filter;
    qq('.chip.ctrl', filters).forEach(b=>b.classList.toggle('is-active', b===btn));
    qq('.card', grid).forEach(card=>{
      const badge = (card.dataset.badge || '').toLowerCase();
      const pop   = card.dataset.popular === '1';
      const open  = card.dataset.open === '1';
      let show = true;
      if(val === 'VIP') show = (badge === 'vip');
      else if(val === 'Popular') show = pop;
      else if(val === 'Open') show = open;
      card.hidden = !show;
    });
    info('tier_filter', { filter: val });
  });

  // Compare popovers
  let lastTrigger = null;
  on(root, 'click', (e)=>{
    const btn = e.target.closest('.compare-btn');
    if(!btn) return;
    const card = btn.closest('.card');
    const key  = card?.dataset?.tier || btn.getAttribute('data-compare');
    const pop  = root.querySelector(`.compare-popover[data-for="${key}"]`);
    if(!pop) return;
    const open = pop.hidden;
    pop.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    if(open) lastTrigger = btn;
    info('compare_toggle', { tier:key, open });
  });
  on(document, 'click', (e)=>{
    const pop = q('.compare-popover:not([hidden])');
    if(!pop) return;
    if(!e.target.closest('.compare-popover') && !e.target.closest('.compare-btn')){
      pop.hidden = true; lastTrigger?.setAttribute('aria-expanded','false');
    }
  });
  on(document, 'keydown',(e)=>{
    if(e.key === 'Escape'){
      const pop = q('.compare-popover:not([hidden])');
      if(pop){ pop.hidden = true; lastTrigger?.setAttribute('aria-expanded','false'); lastTrigger?.focus(); }
    }
  });
}

// -------------------------
// 7) UTM/src stitching
// -------------------------
function stitchAttribution(){
  if(!CFG.enrichUTM) return;
  try{
    const p = new URLSearchParams(location.search);
    const utm = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content'];
    const src = p.get('src') || document.referrer || 'direct';

    const rewrite = (a) => {
      const href = a.getAttribute('href');
      if(!href) return;
      const u = new URL(href, location.origin);
      u.searchParams.set('src', src.slice(0,80));
      utm.forEach(k=>{ if(p.get(k)) u.searchParams.set(k, p.get(k)); });
      a.setAttribute('href', u.toString());
    };

    qq(CFG.donateSelector).forEach(rewrite);
    qq(CFG.sponsorSelector).forEach(rewrite);
    info('utm_stitched');
  }catch(e){ warn('utm_stitch_error', e?.message); }
}

// -------------------------
// 8) A11y autofixes & checks
// -------------------------
function a11yAutofix(){
  if(!CFG.ariaAutofix) return;
  // 8.1 buttons without type => type="button"
  qq('button:not([type])').forEach(b=>{
    b.setAttribute('type','button'); logFix('button_type_added', b.outerHTML.slice(0,120));
  });
  // 8.2 images missing alt => alt=""
  qq('img:not([alt])').forEach(img=>{
    img.setAttribute('alt',''); logFix('img_alt_empty_added', img.src||'');
  });
  // 8.3 <a> without href role=button gets role and tabindex
  qq('a:not([href])').forEach(a=>{
    if(!a.hasAttribute('role')){ a.setAttribute('role','button'); logFix('a_role_button', a.textContent.trim().slice(0,40)); }
    if(!a.hasAttribute('tabindex')) a.setAttribute('tabindex','0');
  });
  // 8.4 duplicate IDs (flag only)
  const ids = {};
  qq('[id]').forEach(el=>{
    const id = el.id;
    if(ids[id]){ warn('duplicate_id', { id, nodes:[ids[id], el] }); }
    ids[id] = el;
  });
  // 8.5 links opening new window but no label hint (flag)
  qq('a[target="_blank"]').forEach(a=>{
    const aria = (a.getAttribute('aria-label')||'') + ' ' + (a.title||'');
    if(!/\bnew window\b|\bnew tab\b/i.test(aria.trim())){
      warn('new_window_label_missing', { html: a.outerHTML.slice(0,120) });
    }
  });
}

// -------------------------
// 9) Boot + Reporting
// -------------------------
function boot(){
  setNoopenerForExternalTargets();
  addLazyToImages();
  stripePreconnect();

  initStickyHeader();
  initFloatingDonate();
  initHotkeys();
  initShare();
  initDonateRuntime();
  initTiers();
  stitchAttribution();
  a11yAutofix();

  // Final report
  try{
    // eslint-disable-next-line no-console
    console.groupCollapsed('%cFundChamps Auto-Enhance','background:#111;color:#facc15;padding:2px 6px;border-radius:4px');
    console.log('Config:', CFG);
    if(report.fixes.length){ console.table(report.fixes); }
    if(report.warnings.length){ console.warn('Warnings:', report.warnings); }
    if(report.info.length){ console.log('Info:', report.info); }
    console.groupEnd();
  }catch(_){}
  if(CFG.reportToWindow) globalThis.FundChampsReport = report;
}

if(document.readyState === 'loading'){
  document.addEventListener('DOMContentLoaded', boot, { once:true });
}else{
  boot();
}

export { boot, report as FundChampsReport };


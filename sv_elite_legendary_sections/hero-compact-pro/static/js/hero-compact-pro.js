/*!
 * Hero Compact-Pro v7.9 (CSP-safe)
 * - External JS module, no inline scripts/styles required
 */
(function(){
  const reduce = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Tilt (optional, if global fcTiltInit exists) */
  try { if (window.fcTiltInit) window.fcTiltInit(document); } catch {}

  /* Accent & focal crop via data-* */
  try{
    const hero = document.getElementById('fc-hero');
    if (hero){
      hero.style.setProperty('--img-x', hero.getAttribute('data-focal-x') || '50%');
      hero.style.setProperty('--img-y', hero.getAttribute('data-focal-y') || '28%');
      const accent = hero.getAttribute('data-accent') || '#facc15';
      hero.style.setProperty('--accent', accent);
    }
  }catch{}

  /* Reveal */
  if (!reduce){
    try{
      const io = new IntersectionObserver((ents)=>{
        for (const ent of ents) if (ent.isIntersecting){ ent.target.classList.add('in'); io.unobserve(ent.target); }
      }, { rootMargin: '-10% 0px', threshold: .2 });
      document.querySelectorAll('#fc-hero [data-anim]').forEach(el=>io.observe(el));
      addEventListener('pagehide', ()=>io.disconnect(), { once:true });
    }catch{}
  } else {
    document.querySelectorAll('#fc-hero [data-anim]').forEach(el=>el.classList.add('in'));
  }

  /* Share */
  const shareBtn = document.getElementById('hero-share');
  shareBtn?.addEventListener('click', async () => {
    const live = document.getElementById('share-live');
    try{
      const payloadRaw = shareBtn.getAttribute('data-share') || '{}';
      const payload = JSON.parse(payloadRaw.replace(/&quot;/g,'"'));
      try{ if (window.fc?.makeTrackedUrl) payload.url = window.fc.makeTrackedUrl(payload.url || location.href, { from:'hero' }); }catch{}
      if (navigator.share){ await navigator.share(payload); live && (live.textContent='Shared.'); return; }
      await navigator.clipboard.writeText(payload.url || location.href);
      live && (live.textContent='Link copied to clipboard.');
      const t=shareBtn.textContent; shareBtn.textContent='Copied!'; setTimeout(()=>{ shareBtn.textContent=t; live&&(live.textContent=''); },1100);
    }catch{}
  }, { passive:true });

  /* Meter logic */
  const fill = document.querySelector('#fc-hero .hm-fill');
  const raisedEl = document.querySelector('#fc-hero .hm-raised');
  const goalEl   = document.querySelector('#fc-hero .hm-goal');
  const pctEl    = document.querySelector('#fc-hero .hm-pct');
  const meter    = document.querySelector('#fc-hero .meter');

  const nf = (function(){
    try {
      return new Intl.NumberFormat(navigator.language || 'en-US', { style:'currency', currency:'USD' });
    } catch { return null; }
  })();
  const fmt = n => nf ? nf.format(Number(n||0)) : ('$'+Number(n||0).toLocaleString());

  function setProgress(raised, goal){
    goal=Math.max(1,Number(goal||0)); raised=Math.max(0,Number(raised||0));
    const pct=Math.min(100,(raised/goal)*100);
    if (fill) fill.style.setProperty('--p', pct+'%');
    if (raisedEl) raisedEl.textContent = fmt(raised);
    if (goalEl)   goalEl.textContent   = fmt(goal);
    if (pctEl)    pctEl.textContent    = (Math.round(pct*10)/10)+'%';
    meter?.setAttribute('aria-valuenow', String(Math.round(raised)));
    meter?.setAttribute('aria-valuetext', `${fmt(raised)} raised of ${fmt(goal)} (${(Math.round(pct*10)/10)}%)`);
  }

  (function initProgressFromDataset(){
    try{
      const rail = document.getElementById('donation-rail');
      const raised = Number(rail?.getAttribute('data-raised') || 0);
      const goal   = Number(rail?.getAttribute('data-goal') || 10000);
      setProgress(raised, goal);
    }catch{}
  })();

  addEventListener('fc:meter:update', e=>{ try{ const d=e.detail||{}; setProgress(d.raised,d.goal); }catch{} }, { passive:true });

  /* Optional hydrate from /api/totals */
  (async () => {
    const controller = new AbortController();
    addEventListener('pagehide', () => controller.abort(), { once:true });
    try {
      const r = await fetch('/api/totals', { cache: 'no-store', credentials: 'same-origin', signal: controller.signal });
      if (r.ok) {
        const { total, goal } = await r.json();
        if (typeof total !== 'undefined') setProgress(total, goal);
      }
    } catch {}
  })();

  /* Image fallback */
  const img = document.getElementById('fc-hero-img');
  img?.addEventListener('error', () => {
    const fallback = '/static/images/og_default.jpg';
    if (img.src !== fallback) img.src = fallback;
  }, { passive:true });

  /* Holo glare */
  if (!reduce){
    const frame = document.querySelector('#fc-hero .hero-shell');
    const glare = document.querySelector('#fc-hero .holo-glare');
    frame?.addEventListener('pointermove', (e) => {
      const b = frame.getBoundingClientRect(); const x=((e.clientX-b.left)/b.width)*100; const y=((e.clientY-b.top)/b.height)*100;
      glare?.style.setProperty('--gx', x+'%'); glare?.style.setProperty('--gy', y+'%'); if (glare) glare.style.opacity='.28';
    }, { passive:true });
    frame?.addEventListener('pointerleave', ()=>{ if (glare) glare.style.opacity='0'; }, { passive:true });
  }

  /* Decorate donate links with UTM + amount */
  function decorate(url, extra){
    try{
      const u=new URL(url, location.origin);
      u.searchParams.set('utm_source','hero'); u.searchParams.set('utm_medium','cta'); u.searchParams.set('utm_campaign','fundraiser');
      Object.entries(extra||{}).forEach(([k,v])=>{ if(v!=null&&v!=='') u.searchParams.set(k,v); });
      return u.toString();
    }catch{ return url; }
  }
  function isStripeLink(u){
    try{ const h = new URL(u, location.origin).hostname; return /(^|\.)buy\.stripe\.com$/.test(h); }catch{ return false; }
  }
  document.querySelectorAll('#fc-hero [data-payment-link]')?.forEach(a=>{
    const rewrite = () => { try{
      const base = a.getAttribute('href') || '/donate';
      const amount = a.dataset.amount;
      let href = base;
      if (isStripeLink(base) && amount){
        href = decorate('/donate', { amount });
      } else {
        href = decorate(base, { amount });
      }
      a.setAttribute('href', href);
      window.dispatchEvent(new CustomEvent('fc:donate', { detail:{ source:'hero', amount: amount || null } }));
    }catch{} };
    a.addEventListener('pointerdown', rewrite, { passive:true });
    a.addEventListener('click', rewrite, { passive:true });
  });

  /* QR — peer-aware & lazy */
  const qrEl   = document.getElementById('qr-box');
  const linkEl = document.getElementById('qr-fallback-link');
  if (qrEl && linkEl){
    const BASE = linkEl.getAttribute('href') || '/donate';
    function getPeer(){
      try{
        const qs=new URLSearchParams(location.search);
        if (qs.get('peer')) return qs.get('peer');
        const raw=localStorage.getItem('fc_ref_ctx'); if(!raw) return null;
        const ctx=JSON.parse(raw)||{}; return ctx.data?.peer_slug || ctx.data?.peer || null;
      }catch{ return null; }
    }
    function decorateQR(url, extra){
      try{
        const u=new URL(url, location.origin);
        u.searchParams.set('utm_source','qr'); u.searchParams.set('utm_medium','hero'); u.searchParams.set('utm_campaign','fundraiser');
        Object.entries(extra||{}).forEach(([k,v])=>{ if(v!=null&&v!=='') u.searchParams.set(k,v); });
        return u.toString();
      }catch{ return url; }
    }
    function renderQR(){
      const href=decorateQR(BASE,{ peer:getPeer() });
      linkEl.href=href;
      qrEl.innerHTML='';
      if (window.QRCode){
        try { new QRCode(qrEl,{ text:href, width:120, height:120, correctLevel:QRCode.CorrectLevel.M }); return; } catch {}
      }
      const open = Object.assign(document.createElement('a'), { className:'btn btn-micro btn-gold', href:href, target:'_blank', rel:'noopener noreferrer', textContent:'Open Donate' });
      const copy = Object.assign(document.createElement('button'), { className:'btn btn-micro btn-ghost', textContent:'Copy Link' });
      copy.addEventListener('click', async ()=>{ try{ await navigator.clipboard.writeText(href); copy.textContent='Copied!'; setTimeout(()=>copy.textContent='Copy Link',900); }catch{} }, { passive:true });
      const wrap = document.createElement('div'); wrap.style.display='grid'; wrap.style.gap='.35rem'; wrap.append(open, copy);
      qrEl.append(wrap);
    }
    try{
      const io = new IntersectionObserver((ents)=>{
        if (ents.some(e=>e.isIntersecting)){ renderQR(); io.disconnect(); }
      }, { rootMargin: '100px' });
      io.observe(qrEl);
      addEventListener('pagehide', ()=>io.disconnect(), { once:true });
    }catch{ renderQR(); }
    addEventListener('hashchange', renderQR, { passive:true });
    addEventListener('popstate',  renderQR, { passive:true });
    addEventListener('fc:refctx:update', renderQR, { passive:true });
  }

  /* Scroll cue hides on scroll */
  const cue = document.getElementById('hero-cue');
  const hideCue = ()=> cue?.classList.add('hide');
  cue?.addEventListener('click', ()=>{
    try{ const next = document.querySelector('#fc-hero')?.nextElementSibling; next?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); }catch{}
    hideCue();
  }, { passive:true });
  addEventListener('scroll', ()=>{ if ((scrollY||document.documentElement.scrollTop||0) > 20) hideCue(); }, { passive:true });
})();

/* SV-Elite 7.9.3 module — split-partials */
(() => {
  const reduce = matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Focal crop from data-* */
  try{
    const hero = document.getElementById('fc-hero');
    hero?.style.setProperty('--img-x', hero?.getAttribute('data-focal-x') || '50%');
    hero?.style.setProperty('--img-y', hero?.getAttribute('data-focal-y') || '28%');
  }catch{}

  /* Reveal on view */
  if (reduce) {
    document.querySelectorAll('#fc-hero [data-anim]').forEach(el=>el.classList.add('in'));
  } else {
    try{
      const io = new IntersectionObserver((ents)=>{
        for (const ent of ents) if (ent.isIntersecting){ ent.target.classList.add('in'); io.unobserve(ent.target); }
      }, { rootMargin: '-10% 0px', threshold: .2 });
      document.querySelectorAll('#fc-hero [data-anim]').forEach(el=>io.observe(el));
      addEventListener('pagehide', ()=>io.disconnect(), { once:true });
    }catch{}
  }

  /* Announcement / countdown */
  (function(){
    const bar = document.querySelector('.fc-announce');
    const closeBtn = bar?.querySelector('.a-dismiss');
    const countdown = document.getElementById('hero-countdown');
    closeBtn?.addEventListener('click', ()=> bar?.remove(), { passive:true });
    if (countdown && countdown.dataset.datetime){
      const target = new Date(countdown.dataset.datetime);
      if (!isNaN(target)) {
        const tick = () => {
          const diff = Math.max(0, target - new Date());
          const s = Math.floor(diff/1000);
          const d = Math.floor(s/86400); const h = Math.floor((s%86400)/3600);
          const m = Math.floor((s%3600)/60); const sec = s%60;
          countdown.textContent = diff<=0 ? 'We’re live!' : `Starts in ${String(d).padStart(2,'0')}d ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
          if (diff<=0) clearInterval(iv);
        };
        const iv = setInterval(tick, 1000); tick();
        bar?.setAttribute('data-active','true');
      }
    }
  })();

  /* Share */
  (function(){
    const shareBtn = document.getElementById('hero-share');
    shareBtn?.addEventListener('click', async () => {
      const live = document.getElementById('share-live');
      try{
        const payload = JSON.parse(shareBtn.getAttribute('data-share') || '{}');
        try{ if (window.fc?.makeTrackedUrl) payload.url = window.fc.makeTrackedUrl(payload.url || location.href, { from:'hero' }); }catch{}
        if (navigator.share){ await navigator.share(payload); live && (live.textContent='Shared.'); return; }
        await navigator.clipboard.writeText(payload.url || location.href);
        live && (live.textContent='Link copied.');
        const t=shareBtn.textContent; shareBtn.textContent='Copied!'; setTimeout(()=>{ shareBtn.textContent=t; live&&(live.textContent=''); },1100);
      }catch{}
    }, { passive:true });
  })();

  /* Meter + count-up (targets split nodes) */
  const fill = document.querySelector('#fc-hero .hm-fill');
  const raisedEl = document.querySelector('#fc-hero .hm-raised');
  const goalEl   = document.querySelector('#fc-hero .hm-goal');
  const pctEl    = document.querySelector('#fc-hero .hm-pct');
  const meter    = document.querySelector('#fc-hero .meter');

  const fmt = n => { try{ return '$'+Number(n||0).toLocaleString(); }catch{ return '$'+n; } };
  const countUp = (el, to) => {
    if (!el) return;
    if (reduce){ el.textContent = fmt(to); return; }
    let s=0, st; const dur=900;
    const step=t=>{ if(!st) st=t; const p=Math.min((t-st)/dur,1); const v=Math.floor(s+(to-s)*p); el.textContent=fmt(v); if(p<1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };

  function setProgress(raised, goal){
    goal=Math.max(1,Number(goal||0)); raised=Math.max(0,Number(raised||0));
    const pct=Math.min(100,(raised/goal)*100);
    fill?.style.setProperty('--p', pct+'%');
    countUp(raisedEl, raised);
    if (goalEl)   goalEl.textContent   = fmt(goal);
    if (pctEl)    pctEl.textContent    = (Math.round(pct*10)/10)+'%';
    meter?.setAttribute('aria-valuenow', String(Math.round(raised)));
    meter?.setAttribute('aria-valuetext', `${fmt(raised)} raised of ${fmt(goal)} (${(Math.round(pct*10)/10)}%)`);
  }

  // Init from data attrs
  try{
    const rail = document.querySelector('[data-test="donation-rail"]');
    const r = Number(rail?.getAttribute('data-raised') || 0);
    const g = Number(rail?.getAttribute('data-goal')   || 10000);
    setProgress(r,g);
  }catch{}

  // Live hook + optional /api/totals hydrate
  addEventListener('fc:meter:update', e=>{ try{ const d=e.detail||{}; setProgress(d.raised,d.goal); }catch{} }, { passive:true });
  (async () => {
    const controller = new AbortController();
    addEventListener('pagehide', () => controller.abort(), { once:true });
    try {
      const r = await fetch('/api/totals', { cache: 'no-store', credentials: 'same-origin', signal: controller.signal });
      if (r.ok) {
        const { total, goal } = await r.json();
        if (typeof total !== 'undefined') setProgress(total, goal ?? Number(goalEl?.dataset.value||0));
      }
    } catch {}
  })();

  /* Decorate donate links with UTM + amount */
  function decorate(url, extra){
    try{
      const u=new URL(url, location.origin);
      u.searchParams.set('utm_source','hero'); u.searchParams.set('utm_medium','cta'); u.searchParams.set('utm_campaign','fundraiser');
      Object.entries(extra||{}).forEach(([k,v])=>{ if(v!=null&&v!=='') u.searchParams.set(k,v); });
      return u.toString();
    }catch{ return url; }
  }
  document.querySelectorAll('#fc-hero [data-payment-link]')?.forEach(a=>{
    a.addEventListener('click', ()=>{ try{
      const href = decorate(a.getAttribute('href')||'/donate', { amount:a.dataset.amount });
      a.setAttribute('href', href);
      window.dispatchEvent(new CustomEvent('fc:donate', { detail:{ source:'hero', amount:a.dataset.amount||null } }));
    }catch{} }, { passive:true });
  });

  /* QR — peer-aware; visible fallback link is separate node */
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
        try { new QRCode(qrEl,{ text:href, width:116, height:116, correctLevel:QRCode.CorrectLevel.M }); return; } catch {}
      }
      // fallback: buttons
      const open = Object.assign(document.createElement('a'), { className:'btn btn-micro btn-gold', href:href, target:'_blank', rel:'noopener noreferrer', textContent:'Open Donate' });
      const copy = Object.assign(document.createElement('button'), { className:'btn btn-micro btn-ghost', textContent:'Copy Link' });
      copy.addEventListener('click', async ()=>{ try{ await navigator.clipboard.writeText(href); copy.textContent='Copied!'; setTimeout(()=>copy.textContent='Copy Link',900); }catch{} }, { passive:true });
      const wrap = document.createElement('div'); wrap.style.display='grid'; wrap.style.gap='.32rem'; wrap.append(open, copy);
      qrEl.append(wrap);
    }
    if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', renderQR); else renderQR();
    addEventListener('hashchange', renderQR, { passive:true });
    addEventListener('popstate',  renderQR, { passive:true });
    addEventListener('fc:refctx:update', renderQR, { passive:true });
  }

  /* Scroll cue */
  const cue = document.getElementById('hero-cue');
  const hideCue = ()=> cue?.classList.add('hide');
  cue?.addEventListener('click', ()=>{
    try{ const next = document.querySelector('#fc-hero')?.nextElementSibling; next?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); }catch{}
    hideCue();
  }, { passive:true });
  addEventListener('scroll', ()=>{ if ((scrollY||document.documentElement.scrollTop||0) > 20) hideCue(); }, { passive:true });
})();

/* SV-Elite Base Core (CSP-safe) */
(() => {
  "use strict";

  // Sticky seam calc (header + ticker)
  if (!window.__fcSeamCore){
    window.__fcSeamCore = true;
    const root=document.documentElement;
    const H=()=>document.getElementById('site-header');
    const T=()=>document.getElementById('sponsor-leaderboard');
    const calc=()=>{ const h=(H()?.offsetHeight||0)+(T()?.offsetHeight||0);
      if(h>0){ root.style.setProperty('--fc-header-h', h+'px'); root.style.setProperty('--sticky-offset', h+'px'); }
    };
    const raf=()=>requestAnimationFrame(calc); raf();
    if('ResizeObserver'in window){ const ro=new ResizeObserver(raf); H()&&ro.observe(H()); T()&&ro.observe(T()); }
    addEventListener('resize', raf, { passive:true }); addEventListener('load', raf, { once:true });
    document.addEventListener?.('htmx:afterSettle', raf);
  }

  // Section reveal micro-interaction
  try{
    const io=new IntersectionObserver((es)=>es.forEach(x=>x.isIntersecting&&x.target.classList.add('is-visible')), { rootMargin:"-10% 0px -5% 0px" });
    document.querySelectorAll('.section').forEach(s=>io.observe(s));
  }catch{}

  // Theme-color sync (matches header scroll + dark mode)
  try{
    const meta=document.getElementById('meta-theme-color');
    if(!meta) return;
    const brand=(getComputedStyle(document.documentElement).getPropertyValue('--brand')||'').trim() || '#f2c94c';
    const setColor=()=>{ meta.setAttribute('content', matchMedia('(prefers-color-scheme: dark)').matches ? '#0b0b0c' : brand); };
    setColor(); matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setColor);
  }catch{}
})();

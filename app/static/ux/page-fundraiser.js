/* Fundraiser page boot */
(function(){
  "use strict";
  // 1) Deep links: #tiers, #sponsor=<Tier>, #impact=<key>, ?ask=<prompt>
  function actOnHash(){
    try{
      const hash=(location.hash||'').slice(1); if(!hash) return;
      if(hash==='tiers'){ document.getElementById('tiers')?.scrollIntoView({behavior:'smooth',block:'start'}); return; }
      const [key, raw] = hash.split('='), val=decodeURIComponent(raw||'');
      if(key==='sponsor' && val){
        const card=[...document.querySelectorAll('#tiers-grid .s-tier-card,[data-tier]')]
          .find(el => (el.dataset.tier||'').toLowerCase()===val.toLowerCase());
        if(card) (card.querySelector('[data-tier-cta]')||card).click();
        document.getElementById('tiers')?.scrollIntoView({behavior:'smooth'});
      }else if(key==='impact' && val){
        window.dispatchEvent(new CustomEvent('fc:impact:focus',{ detail:{ key: val } }));
        document.getElementById('impact')?.scrollIntoView({behavior:'smooth'});
      }
    }catch{}
  }
  addEventListener('hashchange', actOnHash, { passive:true });
  if (location.hash) setTimeout(actOnHash, 60);

  // 2) Concierge ask param (?ask=)
  try{
    const ask=new URLSearchParams(location.search).get('ask'); if(!ask){} else {
      const open=()=>{ try{
        if (window.openConcierge){ window.openConcierge({ prompt: ask }); return; }
        window.dispatchEvent(new CustomEvent('fc:concierge:open', { detail:{ prompt: ask } }));
        try{ localStorage.setItem('fc_concierge_q', ask); }catch{}
      }catch{} };
      (document.readyState==='loading') ? addEventListener('DOMContentLoaded', open, { once:true }) : open();
    }
  }catch{}

  // 3) Section impressions → analytics
  try{
    const io=new IntersectionObserver((ents)=>{
      ents.forEach(ent=>{
        if (!ent.isIntersecting) return;
        const where=ent.target.getAttribute('data-where')||ent.target.id||'section';
        window.fcTrack && window.fcTrack('section_impression',{ where });
        io.unobserve(ent.target);
      });
    }, { rootMargin: "-25% 0px -55% 0px", threshold: 0.01 });
    ['tiers','impact','about'].forEach(id=>{ const n=document.getElementById(id); n && io.observe(n); });
  }catch{}

  // 4) Meter sync from boot data (set in a tiny inline blob)
  try{
    const boot = (window.__FC_INIT__||{}); const raised = +boot.raised||0, goal=+boot.goal||0;
    if (goal>0) window.dispatchEvent(new CustomEvent('fc:meter:update',{ detail:{ raised, goal } }));
  }catch{}

  // 5) Header shadow soften at top
  try{
    const hdr = document.getElementById('site-header');
    if (hdr){
      const onScroll = () => hdr.classList.toggle('is-scrolled', (scrollY||0) > 6);
      addEventListener('scroll', onScroll, { passive: true }); onScroll();
    }
  }catch{}
})();

addEventListener('DOMContentLoaded', ()=>{
  const add=(rel,href,as)=>{ const l=document.createElement('link'); l.rel=rel; l.href=href; if(as) l.as=as; document.head.appendChild(l); };
  const hero=document.querySelector('[data-preload-hero]')?.dataset.preloadHero; if(hero) add('preload', hero, 'image');
  document.querySelectorAll('[data-preload-font]').forEach(n=>add('preload', n.dataset.preloadFont, 'font'));
});

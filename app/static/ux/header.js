function setActive(){
  const path=location.pathname.replace(/\/$/,''); document.querySelectorAll('.nav a').forEach(a=>{
    const href=new URL(a.getAttribute('href'), location.origin).pathname.replace(/\/$/,'');
    a.removeAttribute('aria-current'); if(path===href) a.setAttribute('aria-current','page');
  });
}
function onScroll(){
  const h=document.getElementById('fc-header'); if(!h) return;
  const y=scrollY; h.classList.toggle('shrink', y>8);
}
let open=false, trapPrev;
function drawer(opening){
  const body=document.body, root=document.querySelector('[data-drawer]'); if(!root) return;
  const panel=root.querySelector('.panel'), overlay=document.querySelector('[data-overlay]');
  open=opening; root.classList.toggle('open', open); overlay.classList.toggle('hidden', !open);
  const hb=document.querySelector('[data-nav-toggle]'); hb?.setAttribute('aria-expanded', open?'true':'false');
  if(open){ trapPrev=document.activeElement; panel.setAttribute('tabindex','-1'); panel.focus(); body.style.overflow='hidden'; }
  else{ panel.removeAttribute('tabindex'); body.style.overflow=''; trapPrev&& trapPrev.focus(); }
}
document.addEventListener('DOMContentLoaded', ()=>{
  setActive(); onScroll();
  addEventListener('scroll', onScroll, {passive:true});
  document.querySelectorAll('[data-nav-toggle]').forEach(b=>b.addEventListener('click',()=>drawer(!open)));
  document.querySelector('[data-overlay]')?.addEventListener('click', ()=>drawer(false));
  addEventListener('keydown', e=>{ if(e.key==='Escape' && open){ e.preventDefault(); drawer(false);} });
});

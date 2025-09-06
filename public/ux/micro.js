const rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
function ripple(e){
  const el = e.currentTarget;
  if(rm) return;
  const r = document.createElement('span');
  r.style.position='absolute'; r.style.inset='0'; r.style.borderRadius='inherit';
  r.style.pointerEvents='none'; r.style.background='radial-gradient(circle at '+e.offsetX+'px '+e.offsetY+'px, rgba(255,189,46,.35), transparent 40%)';
  r.style.transition='opacity .6s ease'; el.appendChild(r); requestAnimationFrame(()=>r.style.opacity='0');
  setTimeout(()=>r.remove(), 650);
}
addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('button,[role="button"],.btn,[data-ripple]').forEach(b=>{
    b.style.position=b.style.position||'relative'; b.style.overflow='hidden';
    b.addEventListener('pointerdown', ripple);
    b.addEventListener('mouseenter', ()=>!rm&&(b.style.transform='translateY(-1px)'));
    b.addEventListener('mouseleave', ()=>b.style.transform='');
  });
});

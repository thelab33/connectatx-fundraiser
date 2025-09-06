function animateCount(el){
  const target = +el.dataset.countTo || 0, dur = +(el.dataset.duration||1200);
  const start = performance.now(), from = +(el.textContent.replace(/[^\d.-]/g,'')||0);
  const fmt = new Intl.NumberFormat(undefined,{maximumFractionDigits:0});
  function frame(t){
    const p = Math.min(1,(t-start)/dur), val = from + (target-from)*p*p*(3-2*p);
    el.textContent = (el.dataset.prefix||'') + fmt.format(val) + (el.dataset.suffix||'');
    if(p<1) requestAnimationFrame(frame);
  } requestAnimationFrame(frame);
}
addEventListener('DOMContentLoaded', ()=>{
  const io = new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting && (animateCount(e.target), io.unobserve(e.target))),{threshold:.4});
  document.querySelectorAll('.counter,[data-count-to]').forEach(el=>io.observe(el));
});

addEventListener('DOMContentLoaded', ()=>{
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es=>{
    es.forEach(e=>{
      if(!e.isIntersecting) return; const img=e.target; const src=img.dataset.src; if(!src) return;
      img.src=src; img.addEventListener('load',()=>img.classList.add('loaded'),{once:true}); io.unobserve(img);
    });
  },{rootMargin:'200px'}) : null;
  document.querySelectorAll('img[data-src]').forEach(img=>{
    img.classList.add('blur-up'); if(io) io.observe(img); else img.src=img.dataset.src;
  });
});

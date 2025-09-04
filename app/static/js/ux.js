(function(){
  // Reveal on view (gentle)
  const io = new IntersectionObserver((es)=>{
    es.forEach(e=>{
      if(e.isIntersecting){ e.target.style.transform='translateY(0)'; e.target.style.opacity='1'; io.unobserve(e.target);}
    })
  }, {threshold:.12});
  document.querySelectorAll('.card,.tier').forEach(el=>{
    el.style.transform='translateY(6px)'; el.style.opacity='.001'; el.style.transition='opacity .28s ease, transform .28s ease';
    io.observe(el);
  });

  // Event helper
  window.emit = (name, props={})=>{
    if(window.gtag) gtag('event', name, props);
    if(window.posthog?.capture) posthog.capture(name, props);
  };
  document.addEventListener('click', (e)=>{
    const el = e.target.closest('[data-gtag]');
    if(el) emit(el.dataset.gtag, {text: el.textContent.trim(), id: el.id || null});
  });
})();


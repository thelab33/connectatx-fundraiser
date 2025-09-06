addEventListener('keydown',(e)=>{
  if(e.target && /input|textarea|select/i.test(e.target.tagName)) return;
  if(e.key==='/' ){ e.preventDefault(); document.querySelector('[data-search]')?.focus(); }
  if(e.key==='t' ){ document.querySelector('[data-toggle-theme]')?.click(); }
  if(e.key==='d' ){ location.hash = '#donate'; document.getElementById('donate')?.scrollIntoView({behavior:'smooth',block:'start'}); }
});

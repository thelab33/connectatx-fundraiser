addEventListener('DOMContentLoaded', ()=>{
  const params = new URLSearchParams(location.search); if(!params.get('kiosk')) return;
  const sections = [...document.querySelectorAll('[data-kiosk]')]; if(!sections.length) return;
  let i=0, stop=false; const next=()=>{ if(stop) return; sections[i%sections.length].scrollIntoView({behavior:'smooth',block:'start'}); i++; setTimeout(next, 6500); };
  ['pointerdown','keydown','wheel','touchstart'].forEach(ev=>addEventListener(ev,()=>stop=true,{once:true}));
  next();
});

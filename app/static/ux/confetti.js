const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
function confetti(){ if(RM) return; const frag=document.createDocumentFragment(); const colors=['#ffbd2e','#ffd86b','#fff'];
  for(let i=0;i<28;i++){ const s=document.createElement('span'); s.textContent=['🎉','✨','🥇','⭐'][i%4];
    s.style.cssText=`position:fixed;left:${Math.random()*100}vw;top:-10px;font-size:${14+Math.random()*18}px;
      transition:transform 900ms ease-out, opacity 1200ms; will-change:transform,opacity; z-index:90`;
    requestAnimationFrame(()=>{ s.style.transform=`translateY(${90+Math.random()*90}vh) rotate(${Math.random()*180}deg)`; s.style.opacity='0.1' }); frag.appendChild(s);
    setTimeout(()=>s.remove(),1300);
  } document.body.appendChild(frag);
}
addEventListener('DOMContentLoaded', ()=>{
  const el = document.querySelector('[data-progress][data-goal]'); const fireAttr = document.querySelector('[data-fire="true"]');
  if(fireAttr) confetti();
  if(!el) return; const pct = (+el.dataset.progress||0)/(+el.dataset.goal||1)*100;
  if(pct>=100) confetti();
});

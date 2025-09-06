addEventListener('submit', (e)=>{
  const f=e.target; if(!(f instanceof HTMLFormElement)) return;
  const btn=f.querySelector('button[type="submit"],[type="submit"]'); if(btn && !btn.disabled){ btn.disabled=true; btn.dataset.ripple=''; btn.textContent='Processing…'; }
});

function tick(root, end){
  const t = Math.max(0, end - new Date());
  const d = Math.floor(t/86400000), h = Math.floor(t%86400000/3600000), m = Math.floor(t%3600000/60000), s = Math.floor(t%60000/1000);
  root.querySelector('[data-dd]').textContent = String(d);
  root.querySelector('[data-hh]').textContent = String(h).padStart(2,'0');
  root.querySelector('[data-mm]').textContent = String(m).padStart(2,'0');
  root.querySelector('[data-ss]').textContent = String(s).padStart(2,'0');
}
addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-countdown]').forEach(el=>{
    const end = new Date(el.dataset.countdown);
    el.innerHTML = `
      <div class="countdown">
        <div class="slot"><div class="n" data-dd>0</div><div class="l">days</div></div>
        <div class="slot"><div class="n" data-hh>00</div><div class="l">hrs</div></div>
        <div class="slot"><div class="n" data-mm>00</div><div class="l">min</div></div>
        <div class="slot"><div class="n" data-ss>00</div><div class="l">sec</div></div>
      </div>`;
    tick(el,end); const id=setInterval(()=>tick(el,end),1000); el.addEventListener('remove',()=>clearInterval(id));
  });
});

function setFav(pct){
  const c=document.createElement('canvas'); c.width=c.height=64; const x=c.getContext('2d');
  x.clearRect(0,0,64,64); x.fillStyle='#0000'; x.fillRect(0,0,64,64);
  // ring
  x.lineWidth=8; x.strokeStyle='rgba(0,0,0,.25)'; x.beginPath(); x.arc(32,32,24,0,Math.PI*2); x.stroke();
  x.strokeStyle=getComputedStyle(document.documentElement).getPropertyValue('--brand')||'#ffbd2e';
  x.beginPath(); x.arc(32,32,24,-Math.PI/2,(-Math.PI/2)+Math.PI*2*(pct/100)); x.stroke();
  // text
  x.fillStyle='#fff'; x.font='bold 22px system-ui,Segoe UI'; x.textAlign='center'; x.textBaseline='middle'; x.fillText(String(Math.round(pct)),32,34);
  const link = document.querySelector('link[rel="icon"]') || Object.assign(document.createElement('link'),{rel:'icon'});
  link.href = c.toDataURL('image/png'); document.head.appendChild(link);
}
addEventListener('DOMContentLoaded', ()=>{
  const el = document.querySelector('[data-progress][data-goal]'); if(!el) return;
  const pct = Math.floor((+el.dataset.progress||0)/(+el.dataset.goal||1)*100);
  setFav(Math.max(0,Math.min(100,pct)));
});

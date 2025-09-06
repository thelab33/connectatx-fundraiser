const KEY='fc-ab-vid';
function vid(){ let id=localStorage.getItem(KEY); if(!id){ id=(Math.random().toString(36).slice(2)); localStorage.setItem(KEY,id);} return id;}
function pick(list, salt){ const v=vid()+salt; let h=0; for(let i=0;i<v.length;i++) h=(h*31+v.charCodeAt(i))>>>0; return list[h%list.length]; }
addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-ab]').forEach(el=>{
    // format: data-ab="cta=gold|blue; headline=a|b"
    el.dataset.ab.split(';').map(s=>s.trim()).filter(Boolean).forEach(pair=>{
      const [k,vals]=pair.split('='), options=vals.split('|').map(v=>v.trim());
      const win = pick(options, k); el.classList.add(`${k}-${win}`); el.setAttribute(`data-${k}`, win);
    });
  });
});

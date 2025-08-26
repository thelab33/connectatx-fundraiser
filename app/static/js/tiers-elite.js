(()=>{try{
  const d=document,cards=[...d.querySelectorAll("#tiers .s-tier-card")];
  if(!cards.length) return;
  const emoji={gold:"🥇",silver:"🥈",bronze:"🥉"};
  cards.forEach(card=>{
    const m=card.dataset.tier||"";
    if(!card.querySelector(".s-tier-badge")){
      const b=d.createElement("span"); b.className="s-tier-badge";
      b.textContent=emoji[m]+" "+m.charAt(0).toUpperCase()+m.slice(1); card.appendChild(b);
    }
    card.querySelectorAll("a,button").forEach(btn=>{
      if(/sponsor/i.test(btn.textContent)){
        btn.classList.add("s-tier-cta");
        btn.addEventListener("click",()=>{ try{ localStorage.setItem("fc_last_tier",m);}catch(e){} showSticky(m); });
      }
    });
  });
  function showSticky(name){
    let bar=d.getElementById("tiers-sticky");
    if(!bar){ bar=d.createElement("div"); bar.id="tiers-sticky"; bar.innerHTML='<div class="wrap">Selected: <b></b></div>'; d.body.appendChild(bar); }
    bar.querySelector("b").textContent=name; bar.classList.add("show"); setTimeout(()=>bar.classList.remove("show"),2200);
  }
  const want=(new URLSearchParams(location.search).get("tier")||(localStorage.getItem("fc_last_tier")||"")).toLowerCase();
  if(want){ const hit=cards.find(c=>c.dataset.tier===want); if(hit) hit.classList.add("in-view"); }
  if("IntersectionObserver" in window){
    const io=new IntersectionObserver(ents=>ents.forEach(e=>{ e.target.classList.toggle("in-view", e.isIntersecting); }),{threshold:.15});
    cards.forEach(c=>io.observe(c));
  }
}catch(e){}})();

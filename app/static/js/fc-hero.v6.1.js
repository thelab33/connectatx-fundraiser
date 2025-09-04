/* FC Hero Hydrator — v6.2 (Polished) */
(() => {
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  const hero = $("#fc-hero");
  if (!hero) return;

  /* ---- Config & Intl ---- */
  const locale   = hero.dataset.locale   || "en-US";
  const currency = hero.dataset.currency || "USD";
  const milestones = (hero.dataset.milestones || "25,50,75,100").split(",").map(Number);
  const confettiOn = hero.dataset.confetti === "1";
  const prefersReduced = matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;

  const fmtFull = new Intl.NumberFormat(locale, { style:"currency", currency, maximumFractionDigits:0 });
  const fmtCompact = new Intl.NumberFormat(locale, { style:"currency", currency, notation:"compact", maximumFractionDigits:1 });
  const moneyFmt = (v, opt={}) => (opt.notation==="compact" ? fmtCompact : fmtFull).format(v);

  /* ---- Stats pill ---- */
  function updateStatsPill() {
    const pill = $("#hero-stats-pill", hero);
    if (!pill) return;
    const raised = +pill.dataset.raised || 0;
    const goal   = +pill.dataset.goal   || 0;
    const pct    = Math.max(0, Math.min(100, Math.round(+pill.dataset.pct || (goal ? (raised/goal)*100 : 0))));
    const compact = innerWidth < 420;

    pill.textContent = `${moneyFmt(raised,{notation:compact?"compact":"standard"})} of ${moneyFmt(goal,{notation:compact?"compact":"standard"})} • ${pct}%`;
    pill.setAttribute("aria-label", `Raised ${fmtFull.format(raised)} of ${fmtFull.format(goal)} — ${pct} percent`);
  }

  /* ---- Milestones ---- */
  const fill = $("#hero-fill", hero);
  const msList = $("#hero-milestones", hero);

  function renderMilestones() {
    if (!fill || !msList) return;
    const pct = parseFloat(fill.style.width) || 0;
    msList.innerHTML = milestones.map(m =>
      `<li class="ms${pct >= m ? " hit":""}" data-m="${m}" aria-hidden="true">${m}%</li>`
    ).join("");
    milestones.filter(m => pct >= m).forEach(triggerMilestone);
  }

  function triggerMilestone(m) {
    hero.dispatchEvent(new CustomEvent("fc:milestone",{ detail:{ milestone:m }}));
    if (confettiOn && !prefersReduced && document.visibilityState==="visible") dropConfetti(450);
  }

  /* ---- Countdown ---- */
  const deadlineEl = $("#hero-countdown", hero);
  function initCountdown() {
    if (!deadlineEl?.dataset.deadline) return;
    const end = +new Date(deadlineEl.dataset.deadline);
    if (isNaN(end)) return;

    const fmt2 = n => String(n).padStart(2,"0");
    const tick = () => {
      const d = end - Date.now();
      if (d <= 0) return deadlineEl.textContent = "⏳ ended";
      const days = Math.floor(d/864e5),
            hrs  = Math.floor(d%864e5/36e5),
            mins = Math.floor(d%36e5/6e4);
      deadlineEl.textContent = `⏳ ${fmt2(days)}d : ${fmt2(hrs)}h : ${fmt2(mins)}m`;
    };
    tick();
    setInterval(tick, 3e4);
  }

  /* ---- Share ---- */
  function initShare() {
    const btn = $("#hero-share", hero);
    if (!btn) return;
    btn.addEventListener("click", async () => {
      try {
        const payload = JSON.parse(btn.dataset.share || "{}");
        if (navigator.share) return await navigator.share(payload);
        await navigator.clipboard.writeText(payload.url || location.href);
        const prev = btn.textContent;
        btn.textContent = "✓ Copied";
        setTimeout(()=>btn.textContent=prev, 1400);
      } catch {}
    }, { passive:true });
  }

  /* ---- Match window chip ---- */
  function initMatchChip() {
    const chip = $("#match-chip", hero);
    if (!chip) return;
    const s = new Date(chip.dataset.matchStart||""),
          e = new Date(chip.dataset.matchEnd||"");
    if (isNaN(+s) || isNaN(+e)) return;

    const update = () => {
      const now = new Date(),
            active = now>=s && now<=e;
      chip.classList.toggle("hidden", !active);
      if (active) chip.textContent = `🎯 ${chip.dataset.matchLabel || "Match ×2 Active"}`;
      hero.dispatchEvent(new CustomEvent("fc:match-window",{ detail:{ active, start:s, end:e }}));
    };
    update();
    setInterval(update, 6e4);
  }

  /* ---- CTA ---- */
  function initCTA() {
    const cta = $(".fc-hero-cta", hero);
    if (!cta) return;

    // Autofocus when visible
    new IntersectionObserver(entries=>{
      entries.forEach(e=>{
        if(e.isIntersecting && cta.dataset.autofocusWhenVisible==="1")
          cta.focus({ preventScroll:true });
      });
    },{threshold:.75}).observe(hero);

    // Urgency pulse
    const iso = cta.dataset.urgencyDeadline;
    if (iso) {
      const end = +new Date(iso);
      if (!isNaN(end)) {
        const pulse = () => {
          if (end - Date.now() < 36e5 && !prefersReduced)
            cta.classList.add("cta-pulse");
        };
        pulse();
        setInterval(pulse, 3e4);
      }
    }

    // Hotkey D
    addEventListener("keydown", e=>{
      if((e.key||"").toLowerCase()==="d" && !/input|textarea|select/i.test(e.target.tagName)){
        cta.click(); e.preventDefault();
      }
    },{passive:true});
  }

  /* ---- Layout niceties ---- */
  function placeTitleBelt() {
    const belt = $(".fc-hero-card__belt", hero),
          frame= $(".fc-hero-card__frame", hero),
          h1   = $("#hero-heading", hero);
    if (!belt||!frame||!h1) return;
    const fr=frame.getBoundingClientRect(), hr=h1.getBoundingClientRect();
    const pad = Math.max(16, Math.min(28, fr.width*0.02));
    const beltH = Math.max(56, Math.min(96, hr.height*1.25));
    belt.style.setProperty("--belt-h", beltH+"px");
    belt.style.left = belt.style.right = pad+"px";
    belt.style.top = Math.max(0, hr.top-fr.top+hr.height/2-beltH/2)+"px";
  }

  /* ---- Holo tint ---- */
  async function luminanceTint() {
    try {
      const img=$("#fc-hero-img",hero), tint=$(".fc-hero-card__tint",hero);
      if (!img||!tint) return;
      const probe=new Image();
      probe.crossOrigin="anonymous"; probe.decoding="async";
      probe.src=img.currentSrc||img.src;
      await probe.decode().catch(()=>{});
      const c=document.createElement("canvas");
      c.width=c.height=64;
      const ctx=c.getContext("2d",{willReadFrequently:true});
      if(!ctx) return;
      ctx.drawImage(probe,0,0,c.width,c.height);
      const band=ctx.getImageData(0,Math.floor(c.height*.55),c.width,Math.floor(c.height*.45)).data;
      let L=0,N=0,Rb=0;
      for(let i=0;i<band.length;i+=4){
        const r=band[i]/255,g=band[i+1]/255,b=band[i+2]/255;
        L+=.2126*r+.7152*g+.0722*b;
        Rb+=Math.max(0,r-Math.max(g,b));
        N++;
      }
      const avgL=L/Math.max(1,N), red=Rb/Math.max(1,N)>.12;
      let tintAmt=Math.max(0,Math.min(.45,(avgL-.42)*1.1));
      if(red) tintAmt=Math.max(tintAmt,.35);
      tint.style.setProperty("--tint", String(tintAmt));
      hero.dataset.holoBoost= red?"1":"0";
    } catch {}
  }

  /* ---- Formats (raised/goal) ---- */
  function applyFormats() {
    const compact = innerWidth < 380;
    const raisedEl=$("#hero-raised",hero), goalEl=$("#hero-goal",hero);
    if(raisedEl) raisedEl.textContent=moneyFmt(+raisedEl.dataset.raw||0,{notation:compact?"compact":"standard"});
    if(goalEl) goalEl.textContent=moneyFmt(+goalEl.dataset.raw||0,{notation:compact?"compact":"standard"});
  }

  /* ---- Confetti ---- */
  function dropConfetti(n=500) {
    const root=document.createElement("div");
    Object.assign(root.style,{position:"fixed",inset:"0",pointerEvents:"none",zIndex:"60"});
    document.body.appendChild(root);
    const count=Math.min(n,700);
    for(let i=0;i<count;i++){
      const s=document.createElement("i");
      Object.assign(s.style,{
        position:"absolute",left:Math.random()*100+"%",top:"-2%",
        width:2+Math.random()*4+"px",height:2+Math.random()*4+"px",
        background:"var(--accent,#facc15)",opacity:String(.7+Math.random()*.3),
        transform:`translate3d(0,0,0) rotate(${Math.random()*360}deg)`,
        borderRadius:".5px"
      });
      s.animate([{transform:s.style.transform},{transform:`translate3d(${(Math.random()*2-1)*50}px,100vh,0) rotate(${360+Math.random()*720}deg)`}],{
        duration:2000+Math.random()*1500,easing:"cubic-bezier(.2,.8,.2,1)",fill:"forwards"});
      root.appendChild(s);
    }
    setTimeout(()=>root.remove(),3800);
  }

  /* ---- Init ---- */
  function init(){
    updateStatsPill();
    renderMilestones();
    initCountdown();
    initShare();
    initMatchChip();
    initCTA();
    luminanceTint();
    placeTitleBelt();
    applyFormats();

    // Debounced resize
    let resizeTO;
    addEventListener("resize",()=>{
      clearTimeout(resizeTO);
      resizeTO=setTimeout(()=>{
        updateStatsPill(); applyFormats(); placeTitleBelt();
      },150);
    },{passive:true});
  }

  ("requestIdleCallback" in window)
    ? requestIdleCallback(init,{timeout:1200})
    : setTimeout(init,0);
})();


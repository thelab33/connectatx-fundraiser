/*! FundChamps Widgets — v1.0 (vanilla, CSP-friendly, enterprise-ready) */
export const FCWidgets = (()=>{
  const $  = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));
  const on = (el, ev, fn, opts) => el && el.addEventListener(ev, fn, opts);
  const mm = (q) => (window.matchMedia ? window.matchMedia(q) : { matches:false, addEventListener:()=>{} });
  const fmt = (n, c='USD', l=navigator.language||'en-US') => new Intl.NumberFormat(l, { style:'currency', currency:c, maximumFractionDigits:0 }).format(Math.max(0, Number(n)||0));

  const state = { tickerPaused:false };

  function initTicker(root=document){
    const bar = $('#fc-ticker', root);
    if(!bar) return;
    const list = bar.querySelector('.fc-items');
    const countSpan = bar.querySelector('[data-count]');
    const btnPause = bar.querySelector('[data-pause]');
    const btnPrev  = bar.querySelector('[data-prev]');
    const btnNext  = bar.querySelector('[data-next]');
    const feedUrl  = bar.dataset.src; // optional JSON feed
    let idx=0, items=[]; let iv=null;

    const render = ()=>{
      if(!list) return;
      list.innerHTML = items.map((it)=>{
        const pill = it.pill ? `<span class="fc-chip">${it.pill}</span>` : '';
        const txt  = it.text || '';
        const icon = it.icon ? `<span aria-hidden="true">${it.icon}</span>` : '';
        const href = it.href ? `href="${it.href}" target="_blank" rel="noopener"` : '';
        return `<a class="fc-item" ${href}>${icon}${pill}<span>${txt}</span></a>`;
      }).join('');
      countSpan && (countSpan.textContent = String(items.length));
      bar.classList.toggle('show', items.length>0);
    };

    const rotate = ()=>{
      if(state.tickerPaused || items.length===0) return;
      idx = (idx + 1) % items.length;
      list.scrollTo({ left:list.scrollWidth, behavior:'smooth' });
      setTimeout(()=> list.scrollTo({ left:0 }), 500);
    };

    const start = ()=>{ iv && clearInterval(iv); iv = setInterval(rotate, 4000); };
    const stop  = ()=>{ iv && clearInterval(iv); iv=null; };

    on(btnPause, 'click', ()=>{
      state.tickerPaused = !state.tickerPaused;
      btnPause.setAttribute('aria-pressed', String(state.tickerPaused));
      btnPause.textContent = state.tickerPaused ? '▶' : '⏸';
      state.tickerPaused ? stop() : start();
      document.dispatchEvent(new CustomEvent('fc:ticker:toggle', {detail:{paused:state.tickerPaused}}));
    });

    on(btnPrev, 'click', ()=>{ idx = (idx - 1 + items.length) % items.length; rotate(); });
    on(btnNext, 'click', ()=>{ idx = (idx + 1) % items.length; rotate(); });

    // feed
    (async ()=>{
      try{
        if(feedUrl){
          const res = await fetch(feedUrl, { headers:{'Accept':'application/json'} });
          if(res.ok){
            const json = await res.json();
            if(Array.isArray(json)) items = json;
            else if(Array.isArray(json.items)) items = json.items;
          }
        }
      }catch(e){ console.warn('ticker feed error', e); }
      // fallback: hydrate from inline JSON script (if any)
      if(items.length===0){
        const inline = $('#fc-ticker-data');
        if(inline){
          try{ items = JSON.parse(inline.textContent||'[]'); }catch(e){}
        }
      }
      render(); start();
    })();
  }

  function initQR(root=document){
    const modal = $('#fc-qr', root);
    if(!modal) return;
    const openerSel = '[data-open-qr]';
    const close = modal.querySelector('[data-close]');
    $$(openerSel, root).forEach(o=> on(o, 'click', (e)=>{ e.preventDefault(); modal.hidden=false; modal.removeAttribute('aria-hidden'); }));
    on(close,'click',()=>{ modal.hidden=true; modal.setAttribute('aria-hidden','true'); });
    on(document,'keydown', (e)=>{ if(e.key==='Escape' && !modal.hidden) close.click(); }, { passive:true });
  }

  function initCommandPalette(root=document){
    const modal = $('#fc-cmd', root);
    if(!modal) return;
    const input = modal.querySelector('input');
    const list  = modal.querySelector('ul');
    const close = modal.querySelector('[data-close]');
    const cmds = [
      { id:'donate',  label:'Donate now', kbd:'D', exec:()=> document.querySelector('[data-open-donate-modal]')?.click() },
      { id:'share',   label:'Share campaign', kbd:'S', exec:()=> document.querySelector('#hdr-share')?.click() },
      { id:'leader',  label:'Open leaderboard', kbd:'L', exec:()=> document.getElementById('leaderboard')?.scrollIntoView({behavior:'smooth'}) },
      { id:'pause',   label:'Pause ticker', kbd:'P', exec:()=> document.querySelector('[data-pause]')?.click() }
    ];
    const render = (q='')=>{
      const ql = q.toLowerCase().trim();
      const filtered = cmds.filter(c=> c.label.toLowerCase().includes(ql));
      list.innerHTML = filtered.map(c=> `<li data-id="${c.id}"><span>${c.label}</span><kbd>${c.kbd}</kbd></li>`).join('');
      $$('li', list).forEach(li=> on(li, 'click', ()=>{ const id=li.getAttribute('data-id'); cmds.find(c=>c.id===id)?.exec(); close.click(); }));
    };
    render('');
    on(document,'keydown',(e)=>{
      const k = e.key.toLowerCase();
      if(['d','s','l','p','k'].includes(k) && !e.metaKey && !e.ctrlKey){
        if(k==='k'){ modal.hidden=false; input.value=''; input.focus(); render(''); }
        if(k==='d') cmds[0].exec();
        if(k==='s') cmds[1].exec();
        if(k==='l') cmds[2].exec();
        if(k==='p') cmds[3].exec();
      }
    }, {passive:true});
    on(input,'input',()=> render(input.value));
    on(close,'click',()=>{ modal.hidden=true; });
  }

  // Public init
  function init(root=document){
    initTicker(root);
    initQR(root);
    initCommandPalette(root);
  }

  return { init, initTicker, initQR, initCommandPalette, fmt };
})();

// Auto-init when used via <script type="module">
if (typeof window !== 'undefined'){
  window.FCWidgets = FCWidgets;
  queueMicrotask(()=> FCWidgets.init());
}
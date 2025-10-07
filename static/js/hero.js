/* FUNDCHAMPS-HERO-AUTO */
// Attach behavior to the closest .hero section
const el = document.querySelector('.hero'); if (!el) return;
const id = el.id || 'hero';
const currency = el.dataset.currency || 'USD';
const raised = Number(el.dataset.raised || 0);
const goal = Math.max(1, Number(el.dataset.goal || 1));
const deadlineIso = el.dataset.deadline || '';
const fmt = new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 0 });

const moneyWrap = el.querySelector('.money');
const raisedEl = el.querySelector('[data-role="raised"]');
const goalEl = el.querySelector('[data-role="goal"]');
const pctEl = el.querySelector('[data-role="pct"]');
const meterFill = el.querySelector('.fill');
const meter = el.querySelector('meter');
const deadlineEl = el.querySelector(`#${CSS.escape(id)}-deadline`);
const chips = [...el.querySelectorAll('.chip-btn')];
const donateBtn = el.querySelector(`#${CSS.escape(id)}-donate`);
const donateAmtSpan = donateBtn?.querySelector('.amt');
const monthlyToggle = el.querySelector(`#${CSS.escape(id)}-monthly`);
const shareBtn = el.querySelector(`#${CSS.escape(id)}-share`);
const shareLive = el.querySelector(`#${CSS.escape(id)}-share-live`);

// Values
const pct = Math.min(100, Math.round((raised / goal) * 100));
if (raisedEl) raisedEl.textContent = fmt.format(raised);
if (goalEl) goalEl.textContent = fmt.format(goal);
if (pctEl) pctEl.textContent = `• ${pct}%`;
if (meter) meter.value = raised;
if (meterFill) meterFill.style.setProperty('--p', `${pct}%`);

// Countdown (low CPU)
function tickCountdown(){
  if (!deadlineIso || !deadlineEl) return;
  const end = new Date(deadlineIso); const now = new Date(); const diff = end - now;
  if (Number.isNaN(end.getTime()) || diff <= 0){ deadlineEl.textContent = 'Ends soon'; return; }
  const d = Math.floor(diff / (1000*60*60*24));
  const h = Math.floor((diff / (1000*60*60)) % 24);
  const m = Math.floor((diff / (1000*60)) % 60);
  deadlineEl.textContent = `${d}d ${h}h ${m}m`;
}
tickCountdown(); const timerId = window.setInterval(tickCountdown, 30_000);
window.addEventListener('visibilitychange', () => { if (document.hidden) window.clearInterval(timerId); });

// Quick amount chips + monthly toggle
const storeKey = `donate:${id}`;
function setActiveChip(btn){
  chips.forEach(b => b.setAttribute('aria-pressed', String(b===btn)));
  const amt = Number(btn?.dataset.amt||0);
  const url = new URL(donateBtn.href, location.origin);
  if (amt) url.searchParams.set('amount', String(amt));
  if (monthlyToggle?.checked) url.searchParams.set('interval', 'month'); else url.searchParams.delete('interval');
  donateBtn.href = url.toString();
  if (donateAmtSpan) donateAmtSpan.textContent = amt ? fmt.format(amt) : '';
  localStorage.setItem(storeKey, JSON.stringify({amt, monthly: !!monthlyToggle?.checked}));
}
chips.forEach(b => b.addEventListener('click', () => setActiveChip(b)));
monthlyToggle?.addEventListener('change', () => {
  const active = chips.find(b => b.getAttribute('aria-pressed') === 'true');
  if (active) setActiveChip(active); else {
    const url = new URL(donateBtn.href, location.origin);
    if (monthlyToggle.checked) url.searchParams.set('interval', 'month'); else url.searchParams.delete('interval');
    donateBtn.href = url.toString();
    const state = JSON.parse(localStorage.getItem(storeKey)||'{}');
    localStorage.setItem(storeKey, JSON.stringify({ ...state, monthly: !!monthlyToggle.checked }));
  }
});
// Restore
try{ const state = JSON.parse(localStorage.getItem(storeKey)||'null');
  if (state?.amt){ const match = chips.find(b=>Number(b.dataset.amt)===Number(state.amt)); if (match) setActiveChip(match); }
  if (monthlyToggle && typeof state?.monthly === 'boolean') monthlyToggle.checked = state.monthly;
}catch{}

// Hotkey D to donate (disabled while typing)
function isTyping(){ const a = document.activeElement; return a && (a.tagName==='INPUT' || a.tagName==='TEXTAREA' || a.isContentEditable); }
window.addEventListener('keydown', (e)=>{ if ((e.key==='d'||e.key==='D') && !isTyping()) donateBtn?.click(); });

// Share
shareBtn?.addEventListener('click', async ()=>{
  const title = document.title || 'Support our team'; const url = location.href;
  shareBtn.setAttribute('aria-expanded', 'true');
  try{ if (navigator.share){ await navigator.share({ title, url }); shareLive.textContent = 'Share sheet opened.'; }
       else{ await navigator.clipboard.writeText(url); shareLive.textContent = 'Link copied to clipboard.'; } }
  catch{ shareLive.textContent = 'Share canceled.'; }
  window.setTimeout(()=>{ shareLive.textContent=''; shareBtn.setAttribute('aria-expanded','false'); }, 3000);
});

// Ticker pause/resume if ticker exists
const rail = document.querySelector('.lb__rail');
const pauseBtn = document.querySelector('[data-act="pause"]');
const setPaused = (p)=>{ if (rail) rail.style.animationPlayState = p?'paused':'running'; pauseBtn?.setAttribute('aria-pressed', String(p)); };
pauseBtn?.addEventListener('click', ()=> setPaused(pauseBtn.getAttribute('aria-pressed')!=='true'));
if (rail) new IntersectionObserver(([entry])=> setPaused(!entry.isIntersecting), {threshold:.01}).observe(rail);

// Analytics hook
document.querySelectorAll('[data-cta]')?.forEach(el=>{
  el.addEventListener('click', ()=> window.dispatchEvent(new CustomEvent('cta:click', { detail: { cta: el.getAttribute('data-cta'), id, href: el.href }})));
});

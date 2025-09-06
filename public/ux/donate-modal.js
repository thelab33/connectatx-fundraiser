function openModal(tpl){
  const d=document, o=d.createElement('div'); o.role='dialog'; o.ariaModal='true'; o.className='donate-modal';
  o.innerHTML=tpl; d.body.appendChild(o); const input=o.querySelector('[data-amount]'); input?.focus();
  function close(){ o.remove(); d.body.style.overflow=''; }
  o.addEventListener('click',e=> e.target===o && close());
  d.addEventListener('keydown',e=> e.key==='Escape'&& close(),{once:true});
  d.body.style.overflow='hidden';
}
function template(amount=50){
  return `
  <div class="donate-card glass2 ambient-glow">
    <button class="x" aria-label="Close">✕</button>
    <h3>Back the Season</h3>
    <div class="preset-row">
      ${[25,50,100,250].map(v=>`<button data-preset="${v}">$${v}</button>`).join('')}
      <button data-preset="0">Custom</button>
    </div>
    <label class="amt">$ <input inputmode="numeric" pattern="[0-9]*" data-amount value="${amount}" aria-label="Amount"></label>
    <div class="actions">
      <a class="btn cta-pulse" id="go" href="/payments/checkout?amount=${amount}" data-tip="Secure Stripe Checkout">Donate</a>
    </div>
    <small class="muted">100% secure • tax-deductible where applicable</small>
  </div>`;
}
function hook(){
  document.querySelectorAll('[data-donate-modal]').forEach(btn=>{
    btn.addEventListener('click',e=>{
      e.preventDefault(); const qs=new URL(btn.dataset.url||location.href).searchParams;
      const initial= +(btn.dataset.amount||qs.get('amount')||50);
      openModal(template(initial));
      const M=document.querySelector('.donate-modal'); const amt=M.querySelector('[data-amount]'); const go=M.querySelector('#go');
      M.querySelector('.x').addEventListener('click',()=>M.remove());
      M.querySelectorAll('[data-preset]').forEach(p=>p.addEventListener('click',()=>{
        const v=+p.dataset.preset; if(v>0) amt.value=v; amt.focus(); go.href=`/payments/checkout?amount=${amt.value}`;
      }));
      amt.addEventListener('input',()=> go.href=`/payments/checkout?amount=${amt.value}`);
    });
  });
}
document.addEventListener('DOMContentLoaded', hook);

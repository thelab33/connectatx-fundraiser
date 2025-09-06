function flags(){
  return {
    apple: 'ApplePaySession' in window,
    pr: 'PaymentRequest' in window
  };
}
addEventListener('DOMContentLoaded', ()=>{
  const f=flags(); document.documentElement.dataset.applepay=f.apple?'1':'0';
  document.querySelectorAll('[data-smartpay]').forEach(n=>{
    const msg = f.apple? 'Apple Pay available on this device' : f.pr? 'Fast checkout supported' : '';
    if(msg){ n.textContent = msg; n.classList.remove('hidden'); }
  });
});

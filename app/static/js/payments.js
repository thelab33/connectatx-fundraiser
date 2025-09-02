// app/static/js/payments.js
// Stripe/PayPal glue (CSP-safe, same-origin, no globals required)

const $ = (s, r = document) => r.querySelector(s);
const on = (t, fn, opts) => { window.addEventListener(t, fn, opts); return () => window.removeEventListener(t, fn, opts); };
const fmt$ = (n) => '$' + (Math.round(+n || 0)).toLocaleString();

// ---------- Stripe ----------
const STRIPE_PK = document.querySelector('meta[name="stripe-pk"]')?.content || window.__STRIPE_PK || '';
let stripe, elements, paymentElement;

async function ensureStripeMounted() {
  if (!STRIPE_PK || !window.Stripe) return null;
  if (stripe) return stripe;
  stripe = window.Stripe(STRIPE_PK);
  elements = stripe.elements({ appearance: { theme: 'night' } });
  const host = $('#stripe-payment-element');
  if (host) {
    paymentElement = elements.create('payment', { fields: { billingDetails: 'never' } });
    paymentElement.mount(host);
  }
  return stripe;
}

// open-modal bridge
on('fc:donate:open', (ev) => {
  const amt = ev?.detail?.amount;
  const input = $('#donation-amount');
  if (input && Number.isFinite(+amt)) {
    input.value = String(amt);
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }
  const dlg = document.getElementById('donation-modal');
  if (dlg?.showModal) dlg.showModal();
}, { passive: true });

// Stripe form submit
const form = document.getElementById('sponsor-donation-form');
if (form) {
  form.addEventListener('submit', async (e) => {
    const method = (form.querySelector('input[name="payment_method"]:checked') || {}).value || 'stripe';
    if (method !== 'stripe') return; // let other flows proceed
    e.preventDefault();

    const amount = parseFloat(($('#donation-amount') || {}).value || '0') || 0;
    const name   = ($('#donor-name') || {}).value || 'Supporter';
    const email  = ($('#donor-email') || {}).value || '';
    if (amount <= 0) return;

    await ensureStripeMounted();

    const r = await fetch('/api/payments/stripe/intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        amount,
        name,
        email,
        frequency: (form.querySelector('input[name="frequency"]:checked') || {}).value || 'once',
      }),
    });

    const { client_secret } = await r.json();
    const { error } = await stripe.confirmPayment({
      elements,
      clientSecret: client_secret,
      confirmParams: { return_url: window.location.href },
    });
    if (error) {
      console.error(error.message || error);
      alert('Payment error: ' + (error.message || 'Please try again.'));
    }
  });
}

// “Match this sponsor” fallback (10%)
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-open-donate-modal][data-amount]');
  if (!btn) return;
  const base = parseInt(btn.getAttribute('data-amount') || '0', 10) || 0;
  const amt  = Math.max(10, Math.round(base * 0.10));
  window.dispatchEvent(new CustomEvent('fc:donate:open', { detail: { amount: amt } }));
}, { passive: true });

// ---------- PayPal (SDK must already be on page) ----------
(async () => {
  const host = document.getElementById('paypal-buttons');
  if (!host || !window.paypal) return;

  const input = document.getElementById('donation-amount');
  const getAmt = () => Math.max(1, parseInt((input?.value || '0'), 10) || 0);

  await window.paypal.Buttons({
    createOrder: async () => {
      const r = await fetch('/api/payments/paypal/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ amount: getAmt() }),
      });
      return (await r.json()).id;
    },
    onApprove: async (data) => {
      await fetch(`/api/payments/paypal/capture/${data.orderID}`, { method: 'POST', credentials: 'same-origin' });
      try { window.confetti?.({ particleCount: 120, spread: 70, origin: { y: 0.7 } }); } catch {}
      alert('Thank you! Your sponsorship was captured.');
    },
  }).render('#paypal-buttons');
})();

// ---------- Small ROI pings ----------
const once = (fn) => { let done = false; return (...a) => { if (!done) { done = true; fn(...a); } }; };
const hub = document.getElementById('sponsors-hub');
if (hub && 'IntersectionObserver' in window) {
  const fire = once(() => fetch('/api/metrics/impression', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
    body: JSON.stringify({ key: 'sponsors_hub' }),
  }).catch(() => {}));
  new IntersectionObserver((ents) => ents.forEach(e => { if (e.isIntersecting) fire(); }), { threshold: 0.2 }).observe(hub);
}
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[rel~="sponsored"], a[data-sponsor]');
  if (!a) return;
  fetch('/api/metrics/click', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
    body: JSON.stringify({ key: a.getAttribute('href') || 'sponsor', name: a.getAttribute('data-sponsor-name') || '' }),
  }).catch(() => {});
}, { passive: true });


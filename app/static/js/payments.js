// app/static/js/payments.js
// Stripe + PayPal glue — CSP-safe, same-origin, polished

const $  = (s, r=document) => r.querySelector(s);
const on = (t, fn, opts) => { window.addEventListener(t, fn, opts); return () => window.removeEventListener(t, fn, opts); };
const once = (fn) => { let done=false; return (...a)=>{ if(!done){ done=true; fn(...a); } }; };
const fmt$ = (n) => "$" + Math.round(+n || 0).toLocaleString();

/* ---------- Stripe ---------- */
const STRIPE_PK = document.querySelector('meta[name="stripe-pk"]')?.content || window.__STRIPE_PK || "";
let stripe, elements, paymentElement;

async function ensureStripeMounted() {
  if (!STRIPE_PK || !window.Stripe) return null;
  if (stripe) return stripe;
  stripe = window.Stripe(STRIPE_PK);
  elements = stripe.elements({ appearance:{ theme:"night" } });
  const host = $("#stripe-payment-element");
  if (host) {
    paymentElement = elements.create("payment", { fields:{ billingDetails:"never" } });
    paymentElement.mount(host);
  }
  return stripe;
}

// Modal bridge
on("fc:donate:open", (ev) => {
  const amt = ev?.detail?.amount;
  const input = $("#donation-amount");
  if (input && Number.isFinite(+amt)) {
    input.value = String(amt);
    input.dispatchEvent(new Event("input",{ bubbles:true }));
  }
  const dlg = $("#donation-modal");
  dlg?.showModal?.();
}, { passive:true });

// Stripe form handler
const form = $("#sponsor-donation-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    const method = form.querySelector('input[name="payment_method"]:checked')?.value || "stripe";
    if (method !== "stripe") return; // fallback to PayPal/etc
    e.preventDefault();

    const amount = parseFloat($("#donation-amount")?.value || "0") || 0;
    const name   = $("#donor-name")?.value || "Supporter";
    const email  = $("#donor-email")?.value || "";
    if (amount <= 0) return;

    try {
      await ensureStripeMounted();
      const r = await fetch("/api/payments/stripe/intent", {
        method:"POST",
        headers:{ "Content-Type":"application/json", Accept:"application/json" },
        credentials:"same-origin",
        body: JSON.stringify({
          amount, name, email,
          frequency: form.querySelector('input[name="frequency"]:checked')?.value || "once"
        })
      });

      const { client_secret } = await r.json();
      const { error } = await stripe.confirmPayment({
        elements,
        clientSecret: client_secret,
        confirmParams: { return_url: window.location.href }
      });
      if (error) throw error;
    } catch (err) {
      console.warn("Stripe error", err);
      alert("Payment error: " + (err?.message || "Please try again."));
    }
  });
}

// Quick “match sponsor” shortcut (10%)
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-open-donate-modal][data-amount]");
  if (!btn) return;
  const base = parseInt(btn.getAttribute("data-amount") || "0",10) || 0;
  const amt = Math.max(10, Math.round(base * 0.1));
  window.dispatchEvent(new CustomEvent("fc:donate:open", { detail:{ amount:amt } }));
}, { passive:true });

/* ---------- PayPal ---------- */
(async () => {
  const host = $("#paypal-buttons");
  if (!host || !window.paypal) return;

  const input = $("#donation-amount");
  const getAmt = () => Math.max(1, parseInt(input?.value || "0",10) || 0);

  try {
    await window.paypal.Buttons({
      createOrder: async () => {
        const r = await fetch("/api/payments/paypal/order", {
          method:"POST",
          headers:{ "Content-Type":"application/json", Accept:"application/json" },
          credentials:"same-origin",
          body: JSON.stringify({ amount:getAmt() })
        });
        return (await r.json()).id;
      },
      onApprove: async (data) => {
        await fetch(`/api/payments/paypal/capture/${data.orderID}`, { method:"POST", credentials:"same-origin" });
        try { window.confetti?.({ particleCount:120, spread:70, origin:{ y:.7 } }); } catch {}
        alert("✅ Thank you! Your sponsorship was captured.");
      }
    }).render("#paypal-buttons");
  } catch (err) {
    console.warn("PayPal init failed", err);
  }
})();

/* ---------- ROI pings ---------- */
const hub = $("#sponsors-hub");
if (hub && "IntersectionObserver" in window) {
  const fireImpression = once(() =>
    fetch("/api/metrics/impression", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      credentials:"same-origin",
      body: JSON.stringify({ key:"sponsors_hub" })
    }).catch(()=>{})
  );
  new IntersectionObserver(ents =>
    ents.forEach(e => { if (e.isIntersecting) fireImpression(); }),
    { threshold:.2 }
  ).observe(hub);
}

// Sponsor link clicks
document.addEventListener("click", (e) => {
  const a = e.target.closest('a[rel~="sponsored"], a[data-sponsor]');
  if (!a) return;
  fetch("/api/metrics/click", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    credentials:"same-origin",
    body: JSON.stringify({
      key: a.getAttribute("href") || "sponsor",
      name: a.dataset.sponsorName || ""
    })
  }).catch(()=>{});
}, { passive:true });


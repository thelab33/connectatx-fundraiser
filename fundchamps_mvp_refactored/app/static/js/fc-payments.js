/* eslint-env browser */
/* global Stripe, paypal */
(() => {
  if (window.__fcPayments) return;
  window.__fcPayments = true;

  const has = (k) => typeof k !== "undefined" && k !== null;
  const _money = (n) => Math.round(+n || 0).toLocaleString();

  // Stripe setup (lazy)
  const STRIPE_PK =
    document.querySelector('meta[name="stripe-pk"]')?.content ||
    window.__STRIPE_PK ||
    "";
  let stripe, elements, paymentElement;
  async function ensureStripe() {
    if (!STRIPE_PK || !window.Stripe) return null;
    if (stripe) return stripe;
    stripe = Stripe(STRIPE_PK);
    elements = stripe.elements({ appearance: { theme: "night" } });
    try {
      const peContainer = document.getElementById("stripe-payment-element");
      if (peContainer) {
        paymentElement = elements.create("payment", {
          fields: { billingDetails: "never" },
        });
        paymentElement.mount("#stripe-payment-element");
      }
    } catch (e) {
      console.error("fc-payments catch:", e);
    }
    return stripe;
  }

  // Open modal bridge (your existing partials already emit this)
  window.addEventListener("fc:donate:open", (ev) => {
    // If your modal needs an amount, set it here:
    const amt = ev?.detail?.amount;
    const input = document.querySelector("#donation-amount");
    if (input && has(amt)) {
      input.value = String(amt);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
    // If you have a dialog element with id="donation-modal", show it:
    const dlg = document.getElementById("donation-modal");
    if (dlg && dlg.showModal) dlg.showModal();
  });

  // “Match this sponsor” 10% helper — already wired in the hub via data-amount; fallback here:
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-open-donate-modal][data-amount]");
    if (!btn) return;
    const base = parseInt(btn.getAttribute("data-amount") || "0", 10) || 0;
    const amt = Math.max(10, Math.round(base * 0.1)); // ensure >= $10
    window.dispatchEvent(
      new CustomEvent("fc:donate:open", { detail: { amount: amt } }),
    );
  });

  // Form submit -> create Stripe PI -> confirm
  async function handleStripeSubmit(e) {
    const form = e.currentTarget;
    const method =
      (form.querySelector('input[name="payment_method"]:checked') || {})
        .value || "stripe";
    if (method !== "stripe") return; // let PayPal or server handle
    e.preventDefault();
    const amount =
      parseFloat((form.querySelector("#donation-amount") || {}).value || "0") ||
      0;
    const name = (form.querySelector("#donor-name") || {}).value || "Supporter";
    const email = (form.querySelector("#donor-email") || {}).value || "";
    if (amount <= 0) return;
    await ensureStripe();
    const res = await fetch("/api/payments/stripe/intent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount,
        name,
        email,
        frequency:
          (form.querySelector('input[name="frequency"]:checked') || {}).value ||
          "once",
      }),
    });
    const { client_secret } = await res.json();
    const { error } = await stripe.confirmPayment({
      elements,
      clientSecret: client_secret,
      confirmParams: { return_url: window.location.href },
    });
    if (error) {
      console.error(error.message || error);
      alert("Payment error: " + (error.message || "Please try again."));
    }
  }
  document
    .getElementById("sponsor-donation-form")
    ?.addEventListener("submit", handleStripeSubmit);

  // PayPal Buttons (mount if SDK present)
  if (window.paypal && document.getElementById("paypal-buttons")) {
    const input = document.getElementById("donation-amount");
    const getAmt = () => Math.max(1, parseInt(input?.value || "0", 10) || 0);
    paypal
      .Buttons({
        createOrder: async () => {
          const r = await fetch("/api/payments/paypal/order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: getAmt() }),
          });
          return (await r.json()).id;
        },
        onApprove: async (data) => {
          await fetch(`/api/payments/paypal/capture/${data.orderID}`, {
            method: "POST",
          });
          // Server emits Socket.IO events; add client nudge:
          if (window.confetti)
            window.confetti({
              particleCount: 100,
              spread: 60,
              origin: { y: 0.7 },
            });
          alert("Thank you! Your sponsorship was captured.");
        },
      })
      .render("#paypal-buttons");
  }

  // ROI: impressions & clicks
  const once = (fn) => {
    let done = false;
    return (...a) => {
      if (!done) {
        done = true;
        fn(...a);
      }
    };
  };
  const postJSON = (u, b) =>
    fetch(u, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(b),
    }).catch(() => {});
  const hub = document.getElementById("sponsors-hub");
  if (hub && "IntersectionObserver" in window) {
    const fire = once(() =>
      postJSON("/api/metrics/impression", { key: "sponsors_hub" }),
    );
    new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) fire();
        }),
      { threshold: 0.2 },
    ).observe(hub);
  }
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[rel~="sponsored"], a[data-sponsor]');
    if (a)
      postJSON("/api/metrics/click", {
        key: a.getAttribute("href") || "sponsor",
        name: a.getAttribute("data-sponsor-name") || "",
      });
  });

  // Socket.IO VIP confetti rules
  if (typeof window.io === "function") {
    try {
      const s1 = io("/donations", { transports: ["websocket", "polling"] });
      s1.on("donation", (d) => {
        const a = +d.amount || 0;
        if (window.confetti)
          window.confetti({
            particleCount: Math.min(200, 40 + Math.round(a / 5)),
            spread: 70,
            origin: { y: 0.7 },
          });
        if (window.dataLayer)
          window.dataLayer.push({
            event: "donation",
            amount: a,
            tier: d.tier || "Community",
          });
      });
      const s2 = io("/sponsors", { transports: ["websocket", "polling"] });
      s2.on("sponsor", (d) => {
        const big = (+d.amount || 0) >= 1000;
        if (window.confetti)
          window.confetti({
            particleCount: big ? 220 : 120,
            spread: big ? 90 : 60,
            origin: { y: 0.7 },
          });
        if (window.dataLayer)
          window.dataLayer.push({
            event: "sponsor_spotlight",
            amount: +d.amount || 0,
            tier: d.tier || "Community",
          });
      });
    } catch (e) {
      console.error("fc-payments catch:", e);
    }
  }
})();

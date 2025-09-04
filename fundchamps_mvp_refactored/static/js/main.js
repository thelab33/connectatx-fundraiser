// Main JS entry (ESM). Add analytics, toasts, and small UI helpers here.
export function currency(n, c = "USD") {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: c,
    }).format(n);
  } catch {
    return n;
  }
}
document.addEventListener("DOMContentLoaded", () => {
  // Announcement bar or countdown hooks can live here.
  // Example: console.log('FundChamps ready');
});

(async function () {
        const $ = (id) => document.getElementById(id);
        const set = (el, msg, cls = "") => {
          el.className = `status ${cls}`.trim();
          el.textContent = msg;
        };
        const ms = (t) => `${Math.round(performance.now() - t)}ms`;

        const statusEl = $("status"),
          logEl = $("log");
        const amtIn = $("amount"),
          amtLab = $("amt-label"),
          modeSel = $("mode");
        const tokenIn = $("token"),
          saveBtn = $("save-token");
        const toggleLog = $("toggle-log"),
          cardWrap = $("card-wrap");
        const threeDS = $("threeDS"),
          pubkeyEl = $("pubkey"),
          readyEl = $("ready");
        const idemIn = $("idem"),
          genIdem = $("gen-idem");

        // Log toggle
        toggleLog.addEventListener("click", () => {
          const open = logEl.style.display !== "none";
          logEl.style.display = open ? "none" : "block";
          toggleLog.setAttribute("aria-expanded", String(!open));
          toggleLog.textContent = open ? "Show raw log" : "Hide raw log";
        });
        const log = (x) => {
          logEl.style.display = "block";
          toggleLog.setAttribute("aria-expanded", "true");
          toggleLog.textContent = "Hide raw log";
          logEl.textContent =
            typeof x === "string" ? x : JSON.stringify(x, null, 2);
        };

        // Token & idempotency helpers
        tokenIn.value = localStorage.getItem("dev_api_token") || "";
        saveBtn.onclick = () => {
          localStorage.setItem("dev_api_token", tokenIn.value.trim());
          set(statusEl, "Saved bearer token", "ok");
        };
        genIdem.onclick = () => {
          idemIn.value = "smoke-" + Math.random().toString(36).slice(2, 10);
        };

        // Amount sync + presets
        const syncAmt = () => {
          const v = Math.max(1, parseInt(amtIn.value || "1", 10));
          amtLab.textContent = String(v);
        };
        amtIn.addEventListener("input", syncAmt);
        syncAmt();
        document.querySelectorAll(".preset").forEach((b) =>
          b.addEventListener("click", () => {
            amtIn.value = b.dataset.amt;
            syncAmt();
          }),
        );

        // JSON helper
        const jsonOrText = async (res) => {
          const ct = (res.headers.get("content-type") || "").toLowerCase();
          if (ct.includes("application/json")) return res.json();
          const txt = await res.text();
          throw new Error(`Non-JSON (${res.status}) ${txt.slice(0, 240)}`);
        };

        // 0) Readiness (nice-to-have)
        try {
          const r = await fetch("/api/payments/readiness")
            .then(jsonOrText)
            .catch(() => null);
          if (r && typeof r.stripe_ready === "boolean") {
            readyEl.textContent = r.stripe_ready
              ? "stripe: ready"
              : "stripe: not-configured";
            readyEl.style.borderColor = r.stripe_ready
              ? "rgba(16,185,129,.5)"
              : "rgba(239,68,68,.5)";
          } else {
            readyEl.textContent = "stripe: unknown";
          }
        } catch (_) {}

        // 1) Frontend config
        set(statusEl, "Booting…");
        let stripePk = "";
        try {
          const t0 = performance.now();
          const cfg = await fetch("/api/payments/config").then(jsonOrText);
          stripePk = cfg?.stripe_public_key || "";
          pubkeyEl.textContent = `pk: ${stripePk ? stripePk.replace(/(.{10}).+/, "$1…") : "—"}`;
          if (!stripePk)
            throw new Error("No publishable key from /api/payments/config");
          set(statusEl, `Loaded config in ${ms(t0)}`);
        } catch (e) {
          set(statusEl, e.message || String(e), "err");
          return;
        }

        const stripe = Stripe(stripePk);
        const elements = stripe.elements();
        const card = elements.create("card", { hidePostalCode: false });
        const toggleUI = () => {
          const useElements = modeSel.value === "elements";
          cardWrap.style.display = useElements ? "block" : "none";
          if (useElements && !card._mounted) {
            card.mount("#card-element");
            card._mounted = true;
          }
        };
        modeSel.addEventListener("change", toggleUI);
        toggleUI();

        // 2) Create PI then confirm
        $("pay").addEventListener("click", async () => {
          try {
            const t0 = performance.now();
            set(statusEl, "Creating PaymentIntent…");

            const amount = Math.max(1, parseInt(amtIn.value || "1", 10));
            const headers = { "Content-Type": "application/json" };
            const tok = (localStorage.getItem("dev_api_token") || "").trim();
            if (tok) headers["Authorization"] = "Bearer " + tok;
            const idem = (idemIn.value || "").trim();
            if (idem) headers["Idempotency-Key"] = idem;

            const payload = {
              amount,
              currency: "usd",
              source: "web_smoke",
              description: "Stripe smoke test",
              metadata: { note: ($("note").value || "").slice(0, 120) },
            };

            // NOTE: server route is /payments/stripe/intent (not /api/…)
            const res = await fetch("/payments/stripe/intent", {
              method: "POST",
              headers,
              body: JSON.stringify(payload),
            });
            const data = await jsonOrText(res).catch((e) => {
              throw e;
            });
            log({
              request: "/payments/stripe/intent",
              headers,
              payload,
              response: data,
            });

            if (!res.ok) {
              set(statusEl, data?.error?.message || "Server error", "err");
              return;
            }
            const clientSecret = data.client_secret;
            if (!clientSecret) {
              set(statusEl, "Missing client_secret", "err");
              return;
            }

            set(statusEl, `PI created in ${ms(t0)} — confirming…`);

            // Optional: peek PI (client-side) for quick sanity
            try {
              const peek = await stripe.retrievePaymentIntent(clientSecret);
              if (peek?.paymentIntent) {
                log({
                  ...JSON.parse(logEl.textContent || "{}"),
                  peek: {
                    id: peek.paymentIntent.id,
                    amount: peek.paymentIntent.amount,
                    status: peek.paymentIntent.status,
                    pm_types: peek.paymentIntent.payment_method_types,
                  },
                });
              }
            } catch (_) {}

            let result;
            if (modeSel.value === "headless") {
              // Headless shortcut. If 3-D Secure is checked, use Stripe test PM that requires challenge.
              const pm = threeDS.checked
                ? "pm_card_threeDSecure2Required"
                : "pm_card_visa";
              result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: pm,
              });
            } else {
              result = await stripe.confirmCardPayment(clientSecret, {
                payment_method: { card },
              });
            }

            if (result.error) {
              set(statusEl, `Declined: ${result.error.message}`, "err");
              log(result.error);
              return;
            }
            const pi = result.paymentIntent;
            if (pi?.status === "succeeded") {
              set(
                statusEl,
                `✅ Success! ${pi.id} — $${(pi.amount / 100).toFixed(2)}`,
                "ok",
              );
              log(pi);
            } else if (pi?.status === "requires_action") {
              set(
                statusEl,
                `Action required — handled by Stripe.js. Status: ${pi.status}`,
                "warn",
              );
              log(pi);
            } else {
              set(statusEl, `PI status: ${pi?.status || "unknown"}`, "warn");
              log(pi || result);
            }
          } catch (e) {
            set(statusEl, `Unexpected: ${e.message || e}`, "err");
            log(e.stack || String(e));
          }
        });

        // Motion-safe
        if (
          matchMedia &&
          matchMedia("(prefers-reduced-motion: reduce)").matches
        ) {
          document.documentElement.style.scrollBehavior = "auto";
        }
      })();

#!/usr/bin/env bash
set -euo pipefail

TARGET="app/templates/partials/impact_lockers.html"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$(dirname "$TARGET")"
[[ -f "$TARGET" ]] && cp "$TARGET" "$TARGET.$STAMP.bak" && echo "🔒 Backup: $TARGET.$STAMP.bak"

cat > "$TARGET" <<'__IL_HTML__'
{# ================= FundChamps • Impact Lockers (SV Elite Edition) ================= #}
{# - Self-contained (scoped CSS+JS)
   - A11y complete + reduced motion aware
   - Safe Jinja fallbacks + demo seeding for out-of-box demo
   - Donation modal prefill + analytics events
#}

{% set demo_buckets = [
  {"key":"gym_month","emoji":"🏋️","label":"Gym Access (Month)","details":"Covers open gym + strength training","allocated":1800,"total":3000,"next_gap":75,"next_label":"Next Week Pass"},
  {"key":"tourney_travel","emoji":"🚌","label":"Tournament Travel","details":"Vans, gas, meals on the road","allocated":2200,"total":5000,"next_gap":120,"next_label":"Gas Card"},
  {"key":"scholars","emoji":"📚","label":"Academics & Tutoring","details":"1:1 tutoring & SAT prep","allocated":900,"total":2500,"next_gap":60,"next_label":"Study Kit"},
  {"key":"gear","emoji":"👟","label":"Team Gear","details":"Shoes, uniforms, warm-ups","allocated":3400,"total":4000,"next_gap":50,"next_label":"Socks & Grips"}
] %}

{# Use provided impact_buckets, else seed with demo_buckets for instant demo #}
{% set buckets = impact_buckets if impact_buckets is defined and impact_buckets else demo_buckets %}

<section id="impact-lockers"
  class="relative scroll-mt-28 mx-auto max-w-7xl px-4 sm:px-6 py-14 text-white"
  aria-labelledby="impact-heading"
  data-demo="{{ 'true' if (impact_buckets is not defined or not impact_buckets) else 'false' }}"
>
  <style>
    /* ===== Scoped to #impact-lockers only ===== */
    #impact-lockers::before{
      content:""; position:absolute; inset:-35% -10% auto;
      background: radial-gradient(900px 450px at 60% -10%, rgba(250,204,21,.12), transparent 60%);
      z-index:0;
    }
    #impact-lockers > *{ position:relative; z-index:1; }

    #impact-lockers .fc-card{
      backdrop-filter: blur(10px) saturate(120%);
      -webkit-backdrop-filter: blur(10px) saturate(120%);
      background: linear-gradient(120deg, rgba(255,255,255,.06), rgba(250,220,100,.08));
      border-radius: 1.25rem; border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 10px 32px rgba(250,204,21,.16), 0 2px 10px rgba(0,0,0,.35);
    }
    #impact-lockers .fc-cta{
      background: linear-gradient(90deg, #fde68a, #fbbf24, #fde68a);
      color:#111827; font-weight:900; border-radius:9999px;
      transition: transform .15s ease, box-shadow .15s ease;
      box-shadow: 0 8px 26px rgba(251,191,36,.35);
    }
    #impact-lockers .fc-cta:hover{ transform: translateY(-1px); box-shadow: 0 14px 32px rgba(251,191,36,.45); }
    #impact-lockers .pill{
      display:inline-flex; align-items:center; gap:.35rem; font-size:.72rem; font-weight:800;
      border-radius:9999px; padding:.2rem .55rem; background: rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14);
    }
    #impact-lockers .bar{ height:.75rem; border-radius:9999px; background:#18181b; overflow:hidden; }
    #impact-lockers .bar>span{ display:block; height:100%; background:linear-gradient(90deg,#fde68a,#fbbf24,#fde68a); }
    #impact-lockers .locked{ background:rgba(34,197,94,.18); color:#86efac; font-weight:900; }
    #impact-lockers .note{ font-size:.78rem; color:#d4d4d8 }

    /* Hover lift */
    #impact-lockers .lift{ transition: transform .18s ease; will-change: transform; }
    #impact-lockers .lift:hover{ transform: translateY(-2px) scale(1.01); }

    /* Motion */
    @media (prefers-reduced-motion:no-preference){
      #impact-lockers .fc-card{ animation: il-pop .5s cubic-bezier(.4,1.6,.6,1) both; }
      @keyframes il-pop{ from{opacity:0; transform:scale(.96)} to{opacity:1; transform:scale(1)} }
    }
  </style>

  <header class="mb-8 text-center">
    <h2 id="impact-heading"
        class="mb-3 font-extrabold tracking-tight bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-100 bg-clip-text text-transparent text-[clamp(1.65rem,4vw,2.5rem)]">
      Unlock What Matters — Real Impact Buckets
    </h2>
    <p class="note">
      Every gift locks something concrete for our student-athletes. Pick a bucket and we’ll prefill the exact
      amount to <span class="font-semibold text-yellow-300">lock the next milestone</span>.
    </p>
  </header>

  {% if not buckets %}
    <div class="rounded-xl border border-yellow-400/15 bg-black/40 p-6 text-sm text-zinc-300">
      Buckets are being configured. Please check back soon!
    </div>
  {% else %}
  <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
    {% for b in buckets %}
      {% set alloc = (b.allocated or 0) | float %}
      {% set total = (b.total or 0) | float %}
      {% set pct   = (b.percent if b.percent is defined and b.percent is not none else ( (alloc / total * 100) if total > 0 else 0 )) | round(0) %}
      {% set gap   = (b.next_gap or max(total - alloc, 0)) | round(0) %}
      {% set locked= (pct >= 100 or b.locked) %}
    <article class="fc-card lift rounded-2xl p-5 ring-1 ring-yellow-400/10 bg-zinc-900/80"
             role="group" aria-labelledby="bucket-{{ b.key }}-title">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="text-2xl" aria-hidden="true">{{ b.emoji }}</span>
          <div>
            <h3 id="bucket-{{ b.key }}-title" class="text-lg sm:text-xl font-extrabold text-yellow-200">{{ b.label }}</h3>
            {% if b.details %}<p class="text-xs text-zinc-400 mt-1">{{ b.details }}</p>{% endif %}
          </div>
        </div>

        {% if locked %}
          <span class="inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs locked">LOCKED ✅</span>
        {% else %}
          <span class="pill text-yellow-200/90" title="Remaining to goal">
            ${{ '{:,.0f}'.format((total - alloc) if total > alloc else 0) }} left
          </span>
        {% endif %}
      </div>

      <div class="mt-4" aria-live="polite" aria-atomic="true">
        <div class="flex justify-between text-xs text-zinc-300">
          <span>${{ '{:,.0f}'.format(alloc) }}</span>
          <span>Goal: ${{ '{:,.0f}'.format(total) }}</span>
        </div>
        <div class="bar mt-2" role="progressbar" aria-valuemin="0" aria-valuemax="{{ total|int }}" aria-valuenow="{{ alloc|int }}" aria-label="{{ b.label }} progress">
          <span style="width: {{ pct }}%;"></span>
        </div>
        <p class="mt-2 text-xs font-semibold text-yellow-200">{{ pct }}% funded</p>
        {% if gap > 0 and not locked and b.next_label %}
          <p class="mt-1 text-[11px] text-zinc-400">Only <span class="font-bold text-yellow-200">${{ gap }}</span> to lock <span class="font-bold text-yellow-200">{{ b.next_label }}</span>.</p>
        {% endif %}
      </div>

      {% if b.milestones and not locked %}
      <ul class="mt-3 grid grid-cols-2 gap-2">
        {% for m in b.milestones[:4] %}
          <li class="pill text-yellow-200/90">{{ m.label }} · ${{ '{:,.0f}'.format((m.cost or 0)|float) }}</li>
        {% endfor %}
      </ul>
      {% endif %}

      <div class="mt-4 flex flex-wrap items-center gap-3">
        {% if not locked %}
          <button type="button" class="fc-cta px-5 py-2"
            data-impact-donate
            data-bucket="{{ b.key }}"
            data-amount="{{ gap if gap > 0 else 50 }}"
            data-label="{{ b.label }}"
            aria-label="Donate {{ gap }} dollars to {{ b.label }} to lock {{ b.next_label or 'next milestone' }}">
            Donate ${{ gap if gap > 0 else 50 }} to lock next
          </button>
          <button type="button"
            class="rounded-full bg-zinc-800 px-4 py-2 text-yellow-200 ring-1 ring-yellow-400/20 hover:bg-zinc-700"
            data-impact-donate
            data-bucket="{{ b.key }}"
            data-amount="0"
            data-label="{{ b.label }}"
            aria-label="Open donation modal for {{ b.label }}">
            Choose amount
          </button>
        {% else %}
          <button type="button" class="rounded-full bg-zinc-800 px-4 py-2 text-yellow-200 ring-1 ring-yellow-400/20" disabled>
            Fully funded — thank you!
          </button>
        {% endif %}
      </div>
    </article>
    {% endfor %}
  </div>
  {% endif %}
</section>

<script nonce="{{ csp_nonce() if csp_nonce is defined else '' }}">
(() => {
  const root = document.getElementById('impact-lockers'); if (!root || root.__init) return; root.__init = true;

  const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  const currency = new Intl.NumberFormat(undefined, { style:'currency', currency:'USD', maximumFractionDigits:0 });

  function openDonationModal() {
    const trigger = document.querySelector('[data-modal-open="donation-modal"], [data-modal-open="tiers-modal"], [data-modal-open]');
    if (trigger) { trigger.click(); return true; }
    const dlg = document.getElementById('donation-modal');
    if (dlg?.showModal) { dlg.showModal(); return true; }
    return false;
  }

  function ensureHidden(form, id, name, value){
    let el = document.getElementById(id);
    if (!el) { el = document.createElement('input'); el.type='hidden'; el.id=id; el.name=name; form.appendChild(el); }
    el.value = value;
  }

  root.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-impact-donate]'); if (!btn) return;

    const amount = Math.max(5, Math.round(parseFloat(btn.dataset.amount || '0') || 0)); // $5 min
    const bucket = btn.dataset.bucket || '';
    const label  = btn.dataset.label  || bucket;

    if (!openDonationModal()) console.warn('Donation modal trigger not found.');

    setTimeout(() => {
      const form = document.getElementById('donation-form');
      if (!form) return;

      ensureHidden(form, 'donation-allocation', 'allocation', bucket);
      ensureHidden(form, 'donation-allocation-label', 'allocation_label', label);

      const amtInput = document.getElementById('donation-amount');
      if (amtInput && amount > 0) {
        amtInput.value = String(amount);
        amtInput.dispatchEvent(new Event('input', { bubbles:true }));
      }

      const method = document.getElementById('payment-method');
      if (method && !method.value) method.value = 'stripe';

      window.dispatchEvent(new CustomEvent('impact:select', { detail: { bucket, label, amount } }));
    }, 60);
  });

  // Public API: update one bucket with new numbers (e.g., from sockets)
  window.fcUpdateBucket = function(key, patch){
    const title = document.getElementById(`bucket-${CSS.escape(key)}-title`);
    const card  = title?.closest('.fc-card');
    if (!card || !patch) return;

    const alloc   = Number(patch.allocated ?? NaN);
    const total   = Number(patch.total ?? NaN);
    const percent = Number(patch.percent ?? (isFinite(alloc) && isFinite(total) && total > 0 ? (alloc/total*100) : NaN));
    const locked  = isFinite(percent) && percent >= 100;

    const bar = card.querySelector('.bar>span');
    const meta = card.querySelector('[aria-live]');
    if (isFinite(percent) && bar) bar.style.width = Math.max(0, Math.min(100, percent)) + '%';
    if (meta && isFinite(percent)) meta.setAttribute('aria-label', `${title?.textContent || 'Bucket'} progress ${Math.round(percent)}%`);

    // Amounts
    const spans = card.querySelectorAll('.flex.justify-between.text-xs span');
    if (spans.length === 2) {
      if (isFinite(alloc)) spans[0].textContent = currency.format(alloc);
      if (isFinite(total)) spans[1].textContent = 'Goal: ' + currency.format(total);
    }
    // % label
    const pctEl = card.querySelector('.mt-2.text-xs.font-semibold.text-yellow-200');
    if (pctEl && isFinite(percent)) pctEl.textContent = `${Math.round(percent)}% funded`;

    // Lock state
    let badge = card.querySelector('.locked');
    if (locked) {
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs locked';
        badge.textContent = 'LOCKED ✅';
        card.querySelector('.flex.items-start.justify-between')?.appendChild(badge);
      }
      if (!prefersReduced && typeof window.launchConfetti === 'function') {
        window.launchConfetti({ particleCount: 180, spread: 75 });
      }
    }
  };

  // Optional: replace all buckets at once
  window.fcReplaceBuckets = function(list){
    if (!Array.isArray(list)) return;
    const grid = root.querySelector('.grid');
    if (!grid) return;
    grid.innerHTML = '';
    // For brevity, re-rendering is left to server where possible.
    // Client-side templating could be added here if needed.
  };
})();
</script>
__IL_HTML__

echo "✨ Wrote Silicon Valley–level Impact Lockers to: $TARGET"
echo "✅ Done."

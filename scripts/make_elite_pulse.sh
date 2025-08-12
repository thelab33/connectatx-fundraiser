#!/usr/bin/env bash
set -euo pipefail

TARGET="app/templates/partials/program_stats_and_calendar.html"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$(dirname "$TARGET")"

if [[ -f "$TARGET" ]]; then
  cp "$TARGET" "$TARGET.$STAMP.bak"
  echo "🔒 Backup: $TARGET.$STAMP.bak"
fi

cat > "$TARGET" <<'__PULSE_HTML__'
{# =================== FundChamps • Program Pulse (SV Elite Edition) =================== #}
{#  - Self-contained (scoped CSS+JS)  - Mobile-first  - A11y complete
    - Clean Jinja fallbacks (no bleeding vars)  - Sticky next banner + header
    - CSV / ICS export  - Sorting + Filters  - Safe de-duplication
#}

{# ---- Inputs & safe fallbacks ---- #}
{% set stats = stats if stats is defined and stats else [
  {"label":"GPA Avg","value":3.5},
  {"label":"Student-Athletes","value":22},
  {"label":"Fundraising Goal $","value":"10k"},
  {"label":"Active Sponsors","value":17}
] %}

{% set events = events if events is defined and events else [
  {"date":"2025-07-20","name":"AAU Tournament","location":"East Austin Gym","time":"10:00 AM","is_upcoming":true,"opponent":"All Stars","result":"","highlight":"Opening tourney!","sponsor":null,"type":"Tournament"},
  {"date":"2025-07-22","name":"Team Practice","location":"East Austin Gym","time":"5:00 PM","is_upcoming":false,"opponent":"Scrimmage","result":"W","highlight":"Strong win","sponsor":"Austin Realty","type":"Practice"}
] %}

{% set sponsors_sorted = sponsors_sorted if sponsors_sorted is defined and sponsors_sorted else [] %}
{% set sponsors_total  = sponsors_total  if sponsors_total  is defined else (sponsors_sorted | sum(attribute='amount')) %}
{% set sponsors_count  = sponsors_count  if sponsors_count  is defined else (sponsors_sorted | length) %}

{% set total_slots     = total_slots     if total_slots     is defined else 4 %}
{% set default_logo    = (url_for('static', filename='images/logo.webp') if url_for is defined else '/static/images/logo.webp') %}

<section
  id="program-pulse"
  class="relative scroll-mt-28 overflow-hidden bg-zinc-950/90 py-16 text-white"
  aria-labelledby="pulse-heading"
  data-total="{{ sponsors_total or 0 }}"
  data-count="{{ sponsors_count or 0 }}"
>
  <style>
    /* ===== Scoped to #program-pulse only ===== */
    #program-pulse .container{max-width:min(84rem,92vw);margin-inline:auto;padding-inline:clamp(.75rem,2vw,2rem)}
    #program-pulse .fc-card{
      backdrop-filter: blur(12px) saturate(125%);
      -webkit-backdrop-filter: blur(12px) saturate(125%);
      background: linear-gradient(120deg, rgba(255,255,255,.07), rgba(250,220,100,.08));
      border-radius: 1.25rem; border: 1.5px solid rgba(255,255,255,.12);
      box-shadow: 0 8px 28px rgba(250,204,21,.16), 0 1.5px 10px rgba(255,255,255,.08);
    }
    /* Golden halo */
    #program-pulse::before{
      content:""; position:absolute; inset:-40% -20% auto;
      background:radial-gradient(1200px 600px at 50% -10%,rgba(250,204,21,.12),transparent 60%);
      z-index:0;
    }
    #program-pulse > *{position:relative; z-index:1;}

    #program-pulse table th{ cursor:pointer; user-select:none; }
    #program-pulse table tr[data-upcoming="true"]{ background:rgba(250,204,21,.08); color:#fde68a; font-weight:700; }
    #program-pulse table tr[data-result="W"]{ background:rgba(34,197,94,.10); color:#86efac; }
    #program-pulse table tr[data-result="L"]{ background:rgba(239,68,68,.10); color:#fca5a5; }

    #program-pulse .chip{
      display:inline-flex; align-items:center; gap:.35rem;
      font-size:.7rem; font-weight:800; text-transform:uppercase;
      border-radius:9999px; padding:.15rem .5rem;
      background: rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14);
    }
    #program-pulse .next-banner{
      border:1px dashed rgba(250,204,21,.35); background:rgba(250,204,21,.08);
    }

    /* Table polish */
    #program-pulse table tbody tr{transition:background-color .15s ease}
    #program-pulse table tbody tr:nth-child(even){background:rgba(255,255,255,.03)}
    #program-pulse table tbody tr:hover{background:rgba(255,255,255,.06)}

    /* Mobile: card table */
    @media (max-width: 640px){
      #program-pulse table thead { display:none; }
      #program-pulse table, #program-pulse tbody, #program-pulse tr, #program-pulse td { display:block; width:100%; }
      #program-pulse tbody tr { margin-bottom:.9rem; border-radius:.9rem; border:1px solid rgba(255,255,255,.08); background:rgba(24,24,27,.7); padding:.4rem .2rem; }
      #program-pulse td { padding:.35rem .6rem; }
      #program-pulse td[data-label]::before {
        content: attr(data-label) ": "; font-weight:700; color:#f5f5f4; margin-right:.25rem;
      }
    }
    @media (prefers-reduced-motion:no-preference){
      #program-pulse .fc-card{ animation: fc-pop .6s cubic-bezier(.4,1.6,.6,1) both; }
      @keyframes fc-pop{ from{opacity:0; transform:scale(.96)} to{opacity:1; transform:scale(1)} }
    }
  </style>

  <div class="container">
    <h2 id="pulse-heading" class="mb-8 text-center font-extrabold tracking-tight bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-100 bg-clip-text text-transparent text-[clamp(1.75rem,4vw,2.75rem)] drop-shadow-[0_0_20px_rgba(250,204,21,.25)]">
      🗓️ Connect ATX Elite — Stats & Calendar
    </h2>

    {# ===== Stat badges ===== #}
    {% if stats and stats|length %}
    <ul class="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
      {% for s in stats %}
      <li class="fc-card px-4 py-3 text-center">
        <div class="text-xs uppercase tracking-wide text-yellow-200/80">{{ s.label }}</div>
        <div class="mt-1 text-xl font-extrabold text-yellow-300">{{ s.value }}</div>
      </li>
      {% endfor %}
    </ul>
    {% endif %}

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-12">

      {# ===== Left: Next + Filters + Table ===== #}
      <div class="space-y-6 lg:col-span-8">

        {% if events and events|length %}
        <div class="sticky top-2 z-40 next-banner rounded-2xl p-4 text-sm backdrop-blur-md">
          <div class="flex flex-wrap items-center gap-3">
            <span class="chip">Next</span>
            <div id="next-event-text" role="status" aria-live="polite" class="text-yellow-100 flex-1 min-w-[200px]">Scanning upcoming events…</div>
            <div class="ml-auto flex gap-2">
              <button id="evt-add-ics" type="button" class="rounded-full bg-yellow-400/90 px-3 py-1.5 text-xs font-black text-black hover:bg-yellow-400">
                + Add .ics
              </button>
              <a id="evt-add-gcal" href="#" class="rounded-full border border-yellow-400/70 px-3 py-1.5 text-xs font-black text-yellow-200 hover:bg-zinc-900">
                + Google
              </a>
            </div>
          </div>
        </div>
        {% endif %}

        {% if events and events|length %}
        <div class="w-full flex flex-wrap items-center gap-3 text-sm">
          <div class="flex-1 min-w-[220px]">
            <label for="evt-search" class="sr-only">Search</label>
            <input id="evt-search" type="search" placeholder="Search events, opponents, locations…"
                   class="w-full rounded-lg border border-yellow-400/20 bg-zinc-900/70 px-3 py-2 outline-none ring-0 placeholder:text-zinc-400 focus:border-yellow-400/50" />
          </div>
          <div>
            <label for="evt-type" class="sr-only">Type</label>
            <select id="evt-type" class="rounded-lg border border-yellow-400/20 bg-zinc-900/70 px-3 py-2">
              <option value="">All types</option>
              <option>Tournament</option><option>Game</option><option>Practice</option>
              <option>Scrimmage</option><option>Fundraiser</option>
            </select>
          </div>
          <label class="inline-flex items-center gap-2">
            <input id="evt-upcoming" type="checkbox" class="h-4 w-4 rounded border-yellow-400/40 bg-zinc-900/80" />
            Upcoming only
          </label>
          <div class="ml-auto flex items-center gap-2">
            <button id="evt-export" type="button"
                    class="rounded-full border border-yellow-400/40 bg-black px-4 py-2 font-bold text-yellow-200 hover:bg-zinc-900 shadow-lg ring-1 ring-yellow-400/40">
              ⤓ Export CSV
            </button>
            {% if calendar_ics_url is defined and calendar_ics_url %}
            <a href="{{ calendar_ics_url }}"
               class="rounded-full bg-gradient-to-r from-yellow-400 to-yellow-200 px-5 py-2 font-bold text-black shadow hover:scale-105 ring-1 ring-yellow-400/40">
              Export .ics
            </a>
            {% else %}
            <button id="evt-export-ics" type="button"
              class="rounded-full bg-gradient-to-r from-yellow-400 to-yellow-200 px-5 py-2 font-bold text-black shadow hover:scale-105 ring-1 ring-yellow-400/40">
              Export .ics
            </button>
            {% endif %}
          </div>
        </div>

        <div class="w-full overflow-x-auto rounded-2xl border border-yellow-400/10 bg-zinc-900/90 p-5 shadow-xl md:p-7">
          <table class="min-w-full rounded-xl text-left text-sm" aria-describedby="pulse-heading">
            <thead>
              <tr class="sticky top-20 z-10 border-b border-yellow-400/10 bg-zinc-950/90 backdrop-blur-xl text-yellow-300">
                <th scope="col" class="px-3 py-2" data-sort="date"     aria-sort="none">Date</th>
                <th scope="col" class="px-3 py-2" data-sort="name"     aria-sort="none">Event</th>
                <th scope="col" class="px-3 py-2" data-sort="location" aria-sort="none">Location</th>
                <th scope="col" class="px-3 py-2" data-sort="time"     aria-sort="none">Time</th>
                <th scope="col" class="px-3 py-2" data-sort="result"   aria-sort="none">Result</th>
                <th scope="col" class="px-3 py-2" data-sort="sponsor"  aria-sort="none">Sponsor</th>
              </tr>
            </thead>
            <tbody id="evt-body">
              {% for e in events %}
              {% set res = (e.result or '') %}
              {% set res_u = res|string|upper %}
              {% set upcoming = (e.is_upcoming if e.is_upcoming is defined else None) %}
              <tr class="transition-colors"
                  data-row
                  data-date="{{ e.date }}"
                  data-name="{{ e.name or e.opponent }}"
                  data-location="{{ e.location }}"
                  data-time="{{ e.time }}"
                  data-type="{{ e.type or '' }}"
                  data-result="{{ 'W' if 'W' in res_u else ('L' if 'L' in res_u else '') }}"
                  data-upcoming="{{ 'true' if upcoming else 'auto' }}"
                  data-sponsor="{{ e.sponsor or '' }}">
                <td class="whitespace-nowrap px-3 py-2" data-label="Date">
                  <time datetime="{{ e.date }}T{{ e.time|default('00:00') }}">{{ (e.date|string).replace('-', '/') }}</time>
                </td>
                <td class="px-3 py-2" data-label="Event">
                  {{ e.name or e.opponent }}
                  {% if e.type %}<span class="ml-2 chip">{{ e.type }}</span>{% endif %}
                  {% if e.highlight %}<span class="ml-2 text-xs font-semibold text-yellow-300/90">• {{ e.highlight }}</span>{% endif %}
                </td>
                <td class="px-3 py-2" data-label="Location">{{ e.location }}</td>
                <td class="px-3 py-2" data-label="Time">{{ e.time }}</td>
                <td class="px-3 py-2 font-semibold" data-label="Result">
                  {% if 'W' in res_u %}<span class="text-green-300">🟢 Win</span>
                  {% elif 'L' in res_u %}<span class="text-red-400">🔴 Loss</span>
                  {% elif upcoming %}<span class="text-yellow-200">🟡 Upcoming</span>
                  {% else %}<span class="text-zinc-400">—</span>{% endif %}
                </td>
                <td class="px-3 py-2" data-label="Sponsor">
                  {% if e.sponsor %}
                    <span class="font-bold">{{ e.sponsor }}</span>
                  {% else %}
                    <span class="text-zinc-400">—</span>
                  {% endif %}
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          <div class="mt-4 text-xs text-zinc-400">Times shown in your local timezone.</div>
        </div>
        {% else %}
          <div class="w-full rounded-xl border border-yellow-400/20 bg-black/40 p-6 text-sm text-zinc-300">
            No events yet. Check back soon!
          </div>
        {% endif %}
      </div>

      {# ===== Right: Sponsor summary (lightweight) ===== #}
      <aside class="lg:col-span-4 space-y-6">
        <div class="fc-card gold-shadow p-5 text-sm">
          <h3 class="text-lg font-extrabold text-yellow-300">Sponsor Snapshot</h3>
          <div class="mt-3 grid grid-cols-2 gap-3">
            <div class="rounded-xl border border-yellow-400/20 bg-black/40 p-3">
              <div class="text-xs text-yellow-200/80">Sponsors</div>
              <div id="ss-count" class="mt-1 text-2xl font-black text-yellow-300">{{ sponsors_count or 0 }}</div>
            </div>
            <div class="rounded-xl border border-yellow-400/20 bg-black/40 p-3">
              <div class="text-xs text-yellow-200/80">Total Raised</div>
              <div id="ss-total" class="mt-1 text-2xl font-black text-yellow-300">{{ (sponsors_total or 0) | round(0) }}</div>
            </div>
          </div>
          <p class="mt-3 text-xs text-yellow-100/90">Every dollar supports travel, equipment, and academic resources.</p>
        </div>

        <div aria-hidden="true" class="rounded-2xl border border-yellow-400/10 bg-zinc-900/70 p-4 text-xs text-zinc-300">
          Want a live sponsor wall widget here? Call <code>window.fcAddSponsorPulse({...})</code> from any partial.
        </div>
      </aside>
    </div>
  </div>
</section>

<script nonce="{{ csp_nonce() if csp_nonce is defined else '' }}">
(() => {
  const root = document.getElementById('program-pulse');
  if (!root || root.__init) return; root.__init = true;

  const tbody   = root.querySelector('#evt-body');
  const nextTxt = root.querySelector('#next-event-text');
  const totalEl = root.querySelector('#ss-total');
  const countEl = root.querySelector('#ss-count');

  /* ---------- Helpers ---------- */
  const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  const fmt0 = n => (Math.round(+n||0)).toLocaleString();
  const cmp  = (x,y)=> (x||'').toLowerCase().localeCompare((y||'').toLowerCase());

  function parseRowDate(r){
    const date = (r.dataset.date || '').trim();
    const time = (r.dataset.time || '12:00 PM').trim();
    const normTime = /^\d{1,2}:\d{2}/.test(time) ? time : time.replace(/^(\d{1,2})\s*([ap]m)$/i, '$1:00 $2');
    const d = new Date(`${date} ${normTime}`);
    return isNaN(d) ? new Date(date) : d;
  }

  /* ---------- De-dupe rows ---------- */
  if (tbody) {
    const rows = Array.from(tbody.querySelectorAll('[data-row]'));
    const seen = new Set();
    rows.forEach(r => {
      const key = [
        (r.dataset.date||'').trim().toLowerCase(),
        (r.dataset.time||'').trim().toLowerCase(),
        (r.dataset.name||'').trim().toLowerCase(),
        (r.dataset.location||'').trim().toLowerCase()
      ].join('|');
      if (seen.has(key)) r.remove(); else seen.add(key);
    });
  }

  /* ---------- Localize <time> + mark upcoming ---------- */
  if (tbody) {
    const now = new Date();
    tbody.querySelectorAll('tr[data-row]').forEach(r => {
      const t = r.querySelector('time[datetime]');
      if (t) {
        const iso = t.getAttribute('datetime'); const d = new Date(iso);
        if (!isNaN(d)) {
          const hasTime = /T\d{2}:\d{2}/.test(iso);
          t.textContent = hasTime
            ? d.toLocaleString(undefined, { dateStyle:'medium', timeStyle:'short' })
            : d.toLocaleDateString(undefined, { dateStyle:'medium' });
        }
      }
      if (r.dataset.upcoming === 'auto') {
        r.dataset.upcoming = parseRowDate(r) > now ? 'true' : 'false';
      }
    });
  }

  /* ---------- Next event banner ---------- */
  function rowToEvent(r){
    const title = (r.dataset.name || 'Team Event');
    const loc   = (r.dataset.location || '');
    const start = parseRowDate(r);
    const end   = new Date(start.getTime() + 90*60*1000);
    const fmt = d => d.toISOString().replaceAll('-','').replaceAll(':','').replace('.000','');
    return {
      uid      : cryptoRandom(10) + '@fundchamps',
      dtstamp  : fmt(new Date()),
      dtstart  : fmt(start),
      dtend    : fmt(end),
      summary  : title,
      location : loc
    };
  }

  if (tbody && nextTxt) {
    const rows = Array.from(tbody.querySelectorAll('[data-row]'));
    const upcoming = rows.filter(r => r.dataset.upcoming === 'true');
    if (!upcoming.length) {
      nextTxt.textContent = 'No upcoming events — stay tuned!';
    } else {
      const next = upcoming.sort((a,b)=> parseRowDate(a) - parseRowDate(b))[0];
      const when = next.querySelector('time')?.textContent?.trim() || next.dataset.date;
      const what = (next.dataset.name || '').trim();
      const where= (next.dataset.location || '').trim();
      nextTxt.textContent = `Next: ${what} • ${when} • ${where}`;

      root.querySelector('#evt-add-ics')?.addEventListener('click', ()=>{
        downloadICS([rowToEvent(next)], 'next-event.ics');
      });
      const g = root.querySelector('#evt-add-gcal');
      if (g) g.href = googleCalUrl(rowToEvent(next));
    }
  }

  /* ---------- Filters + sort + export ---------- */
  const search = root.querySelector('#evt-search');
  const selType = root.querySelector('#evt-type');
  const chkUpcoming = root.querySelector('#evt-upcoming');

  const sorters = {
    date:(a,b)=> (parseRowDate(a) - parseRowDate(b)),
    name:(a,b)=> cmp(a.dataset.name,b.dataset.name),
    location:(a,b)=> cmp(a.dataset.location,b.dataset.location),
    time:(a,b)=> cmp(a.dataset.time,b.dataset.time),
    result:(a,b)=> cmp(a.dataset.result,b.dataset.result),
    sponsor:(a,b)=> cmp(a.dataset.sponsor,b.dataset.sponsor),
  };

  function applyFilters(){
    if (!tbody) return [];
    const rows = Array.from(tbody.querySelectorAll('[data-row]'));
    const q = (search?.value||'').trim().toLowerCase();
    const ty = (selType?.value||'').toLowerCase();
    const onlyUp = !!(chkUpcoming?.checked);
    const visible = [];
    rows.forEach((row)=>{
      const matchQ = !q || row.dataset.name.toLowerCase().includes(q)
        || row.dataset.location.toLowerCase().includes(q)
        || row.dataset.sponsor.toLowerCase().includes(q);
      const matchT = !ty || (row.dataset.type||'').toLowerCase() === ty;
      const matchU = !onlyUp || row.dataset.upcoming === 'true';
      const show = matchQ && matchT && matchU;
      row.style.display = show ? '' : 'none';
      if (show) visible.push(row);
    });
    return visible;
  }

  let currentSort = { key:'date', dir:'asc' };
  function sortRows(list){
    if (!tbody) return;
    const k = currentSort.key, dir = currentSort.dir === 'asc' ? 1 : -1;
    const sorted = list.sort((a,b)=> sorters[k](a,b)*dir);
    const frag = document.createDocumentFragment();
    sorted.forEach(r=> frag.appendChild(r));
    tbody.appendChild(frag);
  }
  function setSort(key){
    if (currentSort.key === key) currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
    else currentSort = { key, dir:'asc' };
    root.querySelectorAll('th[data-sort]').forEach(th=>{
      th.setAttribute('aria-sort', th.dataset.sort === currentSort.key ? currentSort.dir : 'none');
      th.title = 'Click to sort ' + (th.getAttribute('aria-sort')==='asc'?'↓':'↑');
      th.tabIndex = 0;
    });
    sortRows(applyFilters());
  }
  root.querySelectorAll('th[data-sort]').forEach(th=>{
    th.addEventListener('click', ()=> setSort(th.dataset.sort));
    th.addEventListener('keydown', (e)=> { if(e.key==='Enter' || e.key===' ') { e.preventDefault(); setSort(th.dataset.sort); }});
    th.tabIndex = 0;
  });
  [search, selType, chkUpcoming].forEach(el=> el?.addEventListener('input', ()=> sortRows(applyFilters())));
  setSort('date');

  /* ---------- Export (CSV / ICS / Google) ---------- */
  root.querySelector('#evt-export')?.addEventListener('click', ()=>{
    const visible = applyFilters();
    const header = ['Date','Event','Location','Time','Result','Sponsor'];
    const lines = [header.join(',')];
    visible.forEach(r=>{
      const cells = Array.from(r.children).slice(0,6).map(td=>{
        const txt = td.innerText.replace(/\s+/g,' ').trim().replace(/"/g,'""');
        return `"${txt}"`;
      });
      lines.push(cells.join(','));
    });
    const blob = new Blob([lines.join('\n')], { type:'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'events.csv';
    document.body.appendChild(a); a.click(); a.remove();
  });

  root.querySelector('#evt-export-ics')?.addEventListener('click', ()=>{
    downloadICS(applyFilters().map(rowToEvent), 'events.ics');
  });

  function downloadICS(events, filename){
    const lines = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//FundChamps//Calendar//EN'];
    events.forEach(e=>{
      lines.push('BEGIN:VEVENT','UID:'+e.uid,'DTSTAMP:'+e.dtstamp,'DTSTART:'+e.dtstart,'DTEND:'+e.dtend,
                 'SUMMARY:'+escapeICS(e.summary));
      if (e.location) lines.push('LOCATION:'+escapeICS(e.location));
      lines.push('END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    const blob = new Blob([lines.join('\r\n')], { type:'text/calendar;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = filename || 'events.ics';
    document.body.appendChild(a); a.click(); a.remove();
  }
  function googleCalUrl(e){
    const qp = new URLSearchParams({
      action:'TEMPLATE', text:e.summary, dates:`${e.dtstart}/${e.dtend}`,
      details:'FundChamps event', location:e.location||'', trp:'true'
    });
    return `https://calendar.google.com/calendar/render?${qp.toString()}`;
  }
  function cryptoRandom(n){
    const chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const arr = new Uint8Array(n);
    (window.crypto||window.msCrypto).getRandomValues(arr);
    return Array.from(arr, v=> chars[v%chars.length]).join('');
  }
  function escapeICS(s){ return String(s).replace(/([,;])/g,'\\$1').replace(/\n/g,'\\n'); }

  /* ---------- Public sponsor API (optional) ---------- */
  function addSponsorCard(payload){
    const curTotal = parseFloat(root.dataset.total || '0');
    const curCount = parseInt(root.dataset.count || '0', 10);
    const nextTotal = curTotal + (parseFloat(payload?.amount)||0);
    const nextCount = curCount + 1;
    root.dataset.total = String(nextTotal);
    root.dataset.count = String(nextCount);
    if (totalEl) totalEl.textContent = fmt0(nextTotal);
    if (countEl) countEl.textContent = String(nextCount);
    if (!prefersReduced && typeof window.launchConfetti === 'function' &&
        ((payload?.tier||'').match(/platinum|gold|vip/i) || (+payload?.amount >= 500))) {
      window.launchConfetti({ particleCount: 180, spread: 75 });
    }
  }
  if (!window.fcAddSponsorPulse) window.fcAddSponsorPulse = addSponsorCard;

})();
</script>
__PULSE_HTML__

echo "✨ Wrote Silicon Valley–level Program Pulse to: $TARGET"
echo "✅ Done."

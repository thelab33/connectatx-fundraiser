(() => {
  'use strict';

  // ———————— 1. Utility Methods ————————
  const utils = {
    /** Throttle calls to a function */
    throttle(fn, delay = 120) {
      let lastTime = 0,
        timeout = null;
      return (...args) => {
        const now = Date.now();
        const remain = delay - (now - lastTime);
        if (remain <= 0) {
          lastTime = now;
          fn(...args);
        } else if (!timeout) {
          timeout = setTimeout(() => {
            timeout = null;
            lastTime = Date.now();
            fn(...args);
          }, remain);
        }
      };
    },
    sanitize(str = '') {
      return String(str).replace(
        /[&<>"']/g,
        (m) =>
          ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
          })[m],
      );
    },

    /** Coerce to number */
    toNumber(input = '0') {
      return parseFloat(String(input).replace(/[^0-9.]/g, '')) || 0;
    },
    /** Focus first focusable child */
    focusFirst(el) {
      if (!el) return;
      const selector = 'a,button,input,select,textarea,[tabindex]:not([tabindex="-1"])';
      const target = el.querySelector(selector);
      target?.focus();
    },
  };

  // ———————— 2. App Core State & DOM ————————
  const state = {
    io: null, // Socket.io instance
    dom: {}, // Cached DOM elements
    tickerIndex: 0, // For FOMO ticker cycling
  };

  const DOM_SELECTORS = {
    backToTop: '#backToTop',
    hamburger: '#hamburger',
    mobileMenu: '#mobile-menu',
    progressBar: '#hero-meter-bar > div, .progress-bar',
    progressPercent: '#hero-meter-percent',
    emojiMilestone: '#emoji-milestone',
    fundsRaised: '#funds-raised, #funds-raised-meter',
    fundsGoal: '#funds-goal, #funds-goal-meter',
    vipToast: '#vip-toast',
    sponsorModal: '#sponsor-spotlight-modal, #sponsor-spotlight-modal-footer',
    sponsorNameEl: '#sponsor-name, #sponsor-name-footer',
    amountEl: '#donation-amount, #hero-donation-amount',
    impactEl: '#impact-message, #hero-impact-message',
    heroHeading: '#hero-heading',
    sponsorLeaderboard: '#sponsor-leaderboard-main',
    fomoTicker: '#fomo-ticker-text',
  };

  function cacheDom() {
    // Query all and save for fast lookup
    Object.keys(DOM_SELECTORS).forEach((key) => {
      const sel = DOM_SELECTORS[key];
      state.dom[key] = document.querySelector(sel);
    });
    // Donation ticker is dynamic, set to null initially
    state.dom.donationTicker = null;
  }

  // ———————— 3. Main App Logic ————————
  const app = {
    /** One-time setup for DOM, events, sockets */
    init() {
      cacheDom();
      this.setupHeroHeading();
      this.setupSocket();
      this.bindEvents();
      this.setupScrollAnimations();
      this.updateProgressMeter();
      this.setupVIPToast();
      this.setupHeroQuotes();
      this.setupLiveImpactPreview();
    },

    // ================= Setup & Bindings =================

    setupHeroHeading() {
      const el = state.dom.heroHeading;
      if (!el) return;
      Object.assign(el.style, {
        opacity: '1',
        visibility: 'visible',
        transition: 'none',
        animation: 'none',
        color: '#d4af37',
        textShadow: '0 0 8px #d4af37cc, 0 4px 12px rgba(212, 175, 55, 0.35)',
      });
    },

    setupSocket() {
      try {
        if (!window.io) throw new Error('No Socket.IO');
        state.io = window.io();
        state.io.on('new_donation', this.handleNewDonation.bind(this));
        state.io.on('new_sponsor', this.handleNewSponsor.bind(this));
      } catch {
        console.warn('⚠️ Socket.IO not available – real-time features disabled.');
      }
    },

    bindEvents() {
      const { backToTop, hamburger, heroHeading } = state.dom;

      backToTop?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
      hamburger?.addEventListener('click', this.toggleMobileNav.bind(this));

      document.addEventListener('click', (e) => {
        const btn = e.target.closest('.copy-quote');
        if (btn) this.copyQuote(btn);
      });

      // Only throttle scroll-bound heading reveals
      window.addEventListener('scroll', utils.throttle(this.revealHeadings.bind(this)), {
        passive: true,
      });
      this.revealHeadings();
      heroHeading?.addEventListener('focus', this.setupHeroHeading.bind(this));
    },

    setupScrollAnimations() {
      if (!('IntersectionObserver' in window)) return;
      const observer = new window.IntersectionObserver(
        (entries, obs) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('in-view', 'animate-sparkle');
              obs.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.4 },
      );
      document
        .querySelectorAll('.badge-glass, .prestige-badge')
        .forEach((el) => observer.observe(el));
    },

    setupVIPToast() {
      const { vipToast } = state.dom;
      if (!vipToast || sessionStorage.getItem('vipToastShown')) return;
      vipToast.textContent =
        '🎉 Welcome! New sponsors will be spotlighted here — you could be next!';
      vipToast.classList.remove('hidden');
      vipToast.setAttribute('role', 'status');
      vipToast.setAttribute('aria-live', 'polite');
      setTimeout(() => vipToast.classList.add('hidden'), 6500);
      sessionStorage.setItem('vipToastShown', '1');
    },

    setupHeroQuotes() {
      if (!Array.isArray(window.heroQuotes) || !window.heroQuotes.length) return;
      const [q] = window.heroQuotes;
      ['hero-quote-text', 'hero-quote-author', 'hero-quote-title'].forEach((id) => {
        const el = document.getElementById(id);
        if (el && q[id.replace('hero-quote-', '')])
          el.innerText = q[id.replace('hero-quote-', '')] || '';
      });
      if (q.avatar) {
        const avatarImg = document.getElementById('hero-quote-avatar');
        avatarImg?.setAttribute('src', q.avatar);
      }
    },

    setupLiveImpactPreview() {
      const { amountEl, impactEl } = state.dom;
      if (!amountEl || !impactEl) return;
      impactEl.setAttribute('role', 'status');
      impactEl.setAttribute('aria-live', 'polite');

      const updateImpactPreview = () => {
        const amount = parseFloat(amountEl.value) || 0;
        let msg = '';
        if (amount >= 150) msg = `🎓 Your $${amount} → one week of gym time for all players!`;
        else if (amount >= 100) msg = `🏀 Your $${amount} → a full scholarship for a player!`;
        else if (amount >= 50) msg = `👕 Your $${amount} → a new team jersey.`;
        else msg = `👍 Every dollar counts — thank you!`;
        impactEl.textContent = msg;
        impactEl.classList.remove('hidden');
      };
      updateImpactPreview();
      amountEl.addEventListener('input', updateImpactPreview, {
        passive: true,
      });
    },

    // ================= Live Updates / Real-time =================

    handleNewDonation(data) {
      if (!data) return;
      const amount = Number(data.amount || 0);
      const name = utils.sanitize(String(data.name || 'Anonymous'));
      this.showDonationTicker(
        `🎉 <b>$${amount.toLocaleString()}</b> from <b>${name}</b> – Thank you!`,
      );
      (window.launchConfetti || this.launchConfetti).call(this);
      this.updateProgressMeter();
    },

    handleNewSponsor(data) {
      if (!data) return;
      const name = utils.sanitize(String(data.name || 'A Generous Donor'));
      this.sponsorAlert(name, 'Champion Sponsor');
      this.openSpotlight(name);
    },

    // ================= Widget / UI Actions =================

    toggleMobileNav() {
      const { mobileMenu, hamburger } = state.dom;
      if (!mobileMenu || !hamburger) return;
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
      if (isOpen) utils.focusFirst(mobileMenu);
    },

    copyQuote(button) {
      const quote = button.dataset.quote || '';
      if (!navigator.clipboard) {
        alert('Copy not supported on this browser.');
        return;
      }
      navigator.clipboard
        .writeText(quote)
        .then(() => {
          const status = button.closest('figure,div,section')?.querySelector('#quote-status');
          if (status) status.textContent = 'Quote copied to clipboard';
          const origText = button.textContent;
          button.textContent = 'Copied!';
          button.classList.add('bg-yellow-300', 'text-black', 'font-bold');
          setTimeout(() => {
            if (status) status.textContent = '';
            button.textContent = origText;
            button.classList.remove('bg-yellow-300', 'text-black', 'font-bold');
          }, 1400);
        })
        .catch(() => alert('Copy failed'));
    },

    revealHeadings() {
      document.querySelectorAll('h1, h2').forEach((el) => {
        if (
          !el.classList.contains('in-view') &&
          el.getBoundingClientRect().top < window.innerHeight - 60
        ) {
          el.style.opacity = '1';
          el.classList.add('in-view');
        }
      });
    },

    updateProgressMeter() {
      const { progressBar, progressPercent, emojiMilestone, fundsRaised, fundsGoal } = state.dom;
      if (!progressBar || !fundsRaised || !fundsGoal) return;
      const raised = utils.toNumber(fundsRaised.textContent);
      const goal = Math.max(utils.toNumber(fundsGoal.textContent), 1);
      const percent = Math.min((raised / goal) * 100, 100).toFixed(1);
      setTimeout(() => {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', String(raised));
        progressBar.setAttribute('aria-valuemin', '0');
        progressBar.setAttribute('aria-valuemax', String(goal));
        if (progressPercent) progressPercent.textContent = `${percent}%`;
        if (emojiMilestone) emojiMilestone.textContent = this.getMilestoneEmoji(percent);
      }, 300);
    },

    getMilestoneEmoji(percent) {
      percent = parseFloat(percent);
      if (percent >= 100) return '🏆';
      if (percent >= 75) return '🚀';
      if (percent >= 50) return '🔥';
      if (percent >= 25) return '🚀';
      return '💤';
    },

    showDonationTicker(msg) {
      let ticker = state.dom.donationTicker;
      if (!ticker) {
        ticker = document.createElement('div');
        ticker.id = 'donation-ticker';
        ticker.className =
          'fixed bottom-8 left-1/2 -translate-x-1/2 bg-yellow-400/95 text-black font-bold px-7 py-3 rounded-2xl shadow-xl z-[9999] text-lg animate-bounce-in';
        ticker.setAttribute('role', 'status');
        ticker.setAttribute('aria-live', 'polite');
        document.body.appendChild(ticker);
        state.dom.donationTicker = ticker;
      }
      ticker.innerHTML = msg;
      ticker.classList.add('show');
      setTimeout(() => ticker.classList.remove('show'), 4000);
    },

    openSpotlight(name = 'A Generous Donor') {
      const { sponsorModal, sponsorNameEl } = state.dom;
      if (!sponsorModal || !sponsorNameEl) return;
      sponsorNameEl.innerHTML = `<span class="text-red-400 font-bold">${utils.sanitize(name)}</span>`;
      sponsorModal.classList.add('show');
      sponsorModal.setAttribute('aria-modal', 'true');
      (window.launchConfetti || this.launchConfetti).call(this);
      setTimeout(() => this.closeSpotlight(), 4000);
    },

    closeSpotlight() {
      const { sponsorModal } = state.dom;
      sponsorModal?.classList.remove('show');
    },

    renderSponsorLeaderboard(sponsors = []) {
      const leaderboard = state.dom.sponsorLeaderboard;
      if (!leaderboard) return;
      if (!sponsors.length) {
        leaderboard.innerHTML = `<div class="col-span-2 text-center text-lg text-gold/80 font-semibold">Be our first sponsor! 🏆</div>`;
        return;
      }
      leaderboard.innerHTML = sponsors
        .map((s, i) => {
          const isTop = i === 0;
          return `
          <div class="rounded-2xl border-4 ${isTop ? 'border-gold bg-gradient-to-r from-gold/20 via-red-700/10 to-white/10 scale-105 shadow-inner-gold animate-pulse' : 'border-white/20 bg-black/40'} shadow-elevated p-5 flex flex-col items-center text-center">
            <span class="text-2xl font-extrabold ${isTop ? 'text-gold drop-shadow' : 'text-white/80'}">${utils.sanitize(s.name)}</span>
            <span class="text-xl font-bold mt-2 ${isTop ? 'text-red-400' : 'text-white/60'}">$${Number(s.amount || 0).toLocaleString()}</span>
            ${isTop ? `<div class="prestige-badge mt-3">🏆 Top Champion</div>` : ''}
          </div>
        `;
        })
        .join('');
    },

    sponsorAlert(name, title = 'Champion Sponsor') {
      document.querySelectorAll('.fundchamps-sponsor-alert')?.forEach((a) => a.remove());
      const alert = document.createElement('div');
      alert.className =
        'fundchamps-sponsor-alert fixed bottom-4 right-4 z-[9999] flex flex-col items-end animate-bounce-in';
      alert.setAttribute('role', 'status');
      alert.setAttribute('aria-live', 'polite');
      alert.innerHTML = `
        <div class="bg-black border-4 border-gold rounded-2xl px-7 py-4 shadow-elevated flex flex-col items-center text-center">
          <img src="/static/images/logo.webp" class="w-12 h-12 mb-2 rounded-full border-2 border-gold shadow-gold-glow" alt="Logo" />
          <span class="text-lg font-bold text-gold mb-2">🔥 NEW SPONSOR ALERT! 🔥</span>
          <span class="text-white font-semibold mb-2">Thank you <b>${utils.sanitize(name)}</b> for supporting the team!</span>
          <span class="prestige-badge">${utils.sanitize(title)} 🏆</span>
        </div>
      `;
      document.body.appendChild(alert);
      setTimeout(() => alert.remove(), 4800);
    },

    launchConfetti() {
      const colors = ['#facc15', '#dc2626', '#fff', '#18181b'];
      for (let i = 0; i < 64; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = `${Math.random() * 100}vw`;
        confetti.style.animationDelay = `${Math.random() * 1.5}s`;
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 1800);
      }
      if (navigator.vibrate) navigator.vibrate([22, 16, 6]);
    },
  };

  /* Countdown (expects #header-countdown[data-deadline]) */
  (function () {
    const el = document.getElementById('header-countdown');
    if (!el) return;
    let deadline;
    try {
      deadline = new Date(JSON.parse(el.dataset.deadline));
    } catch (e) {
      return;
    }
    if (isNaN(deadline)) return;

    function fmt(ms) {
      const s = Math.max(0, Math.floor(ms / 1000));
      const d = Math.floor(s / 86400),
        h = Math.floor((s % 86400) / 3600),
        m = Math.floor((s % 3600) / 60),
        ss = s % 60;
      return `${d}d ${h}h ${m}m ${ss}s`;
    }
    function tick() {
      const ms = deadline - Date.now();
      el.textContent = fmt(ms);
      if (ms <= 0) clearInterval(tid);
    }
    tick();
    const tid = setInterval(tick, 1000);
  })();

  /* Non-inline logo fallback */
  (function () {
    const logo = document.querySelector('#site-header img[alt$=" logo"]');
    if (!logo) return;
    logo.addEventListener(
      'error',
      () => {
        logo.src = '/static/images/logo.webp';
      },
      { once: true },
    );
  })();

  // ———————— 4. Micro-FOMO Ticker ————————
  const tickerData = [
    'Jessica J. donated $25!',
    'Austin Bikes became a Gold Sponsor!',
    'Coach Smith matched donations for 1 hour!',
    'Only 3 VIP slots left for August!',
    'Welcome to our newest sponsor: TechPros!',
  ];

  function updateFomoTicker() {
    const ticker = state.dom.fomoTicker;
    if (!ticker) return;
    ticker.textContent = tickerData[state.tickerIndex % tickerData.length];
    state.tickerIndex++;
  }
  setInterval(updateFomoTicker, 3800);

  // ———————— 5. SaaS Global Exposure for Debug/Dev ————————
  window.FundChampsApp = app; // Power move for future SaaS extensibility

  document.addEventListener('DOMContentLoaded', () => {
    app.init();
    cacheDom();
    updateFomoTicker();
  });
})();

#!/bin/bash
# polish_fundchamps.sh
# Polish your Elite FundChamps homepage for world-class SaaS conversion

set -e

# 1. Find your main file
HTML_FILE="${1:-index.html}"
BACKUP="${HTML_FILE}.bak.$(date +%s)"

echo "🔒 Backing up $HTML_FILE to $BACKUP"
cp "$HTML_FILE" "$BACKUP"

# 2. Enforce container max-width & section breathing
echo "✨ Ensuring .fcx-section has max-width and spacing..."
sed -i '' '/\.fcx-section,/s/$/\
  max-width: 1100px;\
  margin-inline: auto;\
  margin-bottom: 3rem;\
  padding-inline: clamp(14px, 5vw, 36px);/' "$HTML_FILE"

# 3. Upgrade Donate button for highest contrast
echo "🟡 Upgrading Donate CTA to be most visible..."
sed -i '' 's/fcx-btn-accent/fcx-btn-accent fc-pro-cta/g' "$HTML_FILE"

# 4. Inject floating donate CTA if missing
FLOAT_CTA='
<!-- Floating Donate CTA for world-class conversion -->
<div class="fc-float-cta" id="floating-donate-cta" style="display: none;">
  <a class="fc-btn" href="{{ HREF_DONATE }}" target="_blank" rel="noopener noreferrer" data-cta="donate">
    Donate Now →
  </a>
</div>
<script {{ nonce_attr() }}>
(() => {
  const float = document.getElementById("floating-donate-cta");
  const donateBtns = document.querySelectorAll("[data-cta=\'donate\']");
  const check = () => {
    let donateVisible = false;
    donateBtns.forEach(btn => {
      const rect = btn.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) donateVisible = true;
    });
    float.style.display = donateVisible ? "none" : "grid";
  };
  window.addEventListener("scroll", check, { passive: true });
  window.addEventListener("resize", check);
  check();
})();
</script>
'
if ! grep -q 'id="floating-donate-cta"' "$HTML_FILE"; then
  echo "⚡ Injecting floating donate CTA before </body>..."
  sed -i '' "s#</body>#$FLOAT_CTA\n</body>#" "$HTML_FILE"
else
  echo "✅ Floating donate CTA already present."
fi

# 5. Audit for micro-impact and about trust language
echo "🔍 Checking Impact/About for trust copy..."
if ! grep -q "tax-deductible" "$HTML_FILE"; then
  sed -i '' 's#<section id="impact"#<section id="impact" data-trust="Every dollar is tax-deductible and secure!"#' "$HTML_FILE"
fi

# 6. Bonus: Card hover polish
echo "🎨 Injecting card hover polish..."
sed -i '' '/\.fcx-card, .fcx-tier-block .card {/a\
  transition: transform .16s cubic-bezier(.4,1.8,.4,1), box-shadow .23s;\
}\
.fcx-card:hover, .fcx-tier-block .card:hover {\
  transform: translateY(-5px) scale(1.015);\
  box-shadow: 0 16px 40px #facc1540, 0 3px 10px #0001;\
}
' "$HTML_FILE"

echo "🎉 All done! $HTML_FILE is now SaaS-founder-level polished."


import glob
import re
import os

# === CONFIG ===
MAX_WIDTH_CSS = """
/* SaaS Pro Section Polish */
.fcx-section, .fcx-section--hero, .fcx-section--tiers {
  max-width: 1100px;
  margin-inline: auto;
  margin-bottom: 3rem;
  padding-inline: clamp(14px, 5vw, 36px);
}
"""
DONATE_CTA_REGEX = re.compile(r'(<a [^>]*?class="[^"]*?fcx-btn[^"]*?)(?<!fcx-btn-accent)([^"]*?)"(.*?>\s*Donate\b)', re.I)
FLOATING_DONATE_HTML = """
<!-- Floating Donate CTA -->
<div class="fc-float-cta" id="floating-donate-cta" style="display:none; position:fixed;bottom:1.7rem;right:1.7rem;z-index:1999;">
  <a class="fcx-btn fcx-btn-accent fc-pro-cta" href="{{ HREF_DONATE }}" target="_blank" rel="noopener noreferrer" data-cta="donate">
    Donate Now →
  </a>
</div>
<script>
(() => {
  const float = document.getElementById("floating-donate-cta");
  const donateBtns = document.querySelectorAll("[data-cta='donate']");
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
"""

# === POLISH FUNCTION ===
def polish_file(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False
    backup_path = path + ".bak"

    # 1. Add/patch .fcx-section CSS in a <style> tag (if not already)
    if ".fcx-section" not in html:
        if "</head>" in html:
            html = html.replace("</head>", f"<style>{MAX_WIDTH_CSS}</style>\n</head>")
            changed = True
        else:
            # fallback: inject at top
            html = f"<style>{MAX_WIDTH_CSS}</style>\n" + html
            changed = True

    # 2. Upgrade Donate buttons
    def cta_repl(m):
        return f'{m.group(1)} fcx-btn-accent{m.group(2)}"{m.group(3)}'
    new_html, ctas = DONATE_CTA_REGEX.subn(cta_repl, html)
    if ctas > 0:
        html = new_html
        changed = True

    # 3. Inject floating donate CTA if missing
    if 'id="floating-donate-cta"' not in html and "</body>" in html:
        html = html.replace("</body>", f"{FLOATING_DONATE_HTML}\n</body>")
        changed = True

    if changed:
        # Make a backup before overwriting
        if not os.path.exists(backup_path):
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(html)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Polished: {path}")
    else:
        print(f"✔️ Already elite: {path}")

# === BATCH ACROSS YOUR TEMPLATES ===
for file in glob.glob("**/*.html", recursive=True):
    if "/venv/" in file or "/node_modules/" in file or "/site-packages/" in file:
        continue
    polish_file(file)


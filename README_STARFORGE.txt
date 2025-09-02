Starforge UI/UX Pack (SV-ELITE)
=================================

Files in this zip map to your existing Flask project.

WHAT'S INCLUDED
---------------
- app/templates/partials/header_and_announcement.html   (replacement)
- app/templates/partials/section_hero.html              (new hero)
- app/templates/partials/section_tiers.html             (tiers grid)
- app/templates/partials/section_impact.html            (impact buckets)
- app/templates/partials/section_about.html             (testimonials + closer)
- app/templates/partials/footer.html                    (light polish)
- app/static/css/starforge-additions.css                (CSS layer to append/import)
- app/static/js/starforge-snippets.js                   (micro JS)

HOW TO INSTALL
--------------
1) Back up your current partials in `app/templates/partials/`.
2) Copy the files in this zip to the same paths in your repo.
3) Open `app/static/css/input.css` and, at the very END, add:
   @import url("./starforge-additions.css");
4) Ensure base.html points to your compiled CSS (app.min.css) and your JS bundle:
   <link rel="stylesheet" href="{{ asset('css/app.min.css') }}"
     {% if sri('css/app.min.css') %}integrity="{{ sri('css/app.min.css') }}" crossorigin="anonymous"{% endif %}/>
   <script {{ nonce_attr() }} src="{{ asset('js/bundle.min.js') }}" defer
     {% if sri('js/bundle.min.js') %}integrity="{{ sri('js/bundle.min.js') }}" crossorigin="anonymous"{% endif %}></script>
5) Optionally include the micro JS after your bundle if you don't plan to merge it:
   <script src="{{ asset('js/starforge-snippets.js') }}" defer></script>
6) Rebuild CSS:
   npm run css:build   # or `npm run dev` for watch
7) Verify routes render:
   - Hero: `{% block section_hero %}{% include "partials/section_hero.html" %}{% endblock %}`
   - Tiers: `{% block section_tiers %}{% include "partials/section_tiers.html" %}{% endblock %}`
   - Impact: `{% block section_impact %}{% include "partials/section_impact.html" %}{% endblock %}`
   - About: `{% block section_about %}{% include "partials/section_about.html" %}{% endblock %}`

That’s it—polish enabled with no new dependencies.

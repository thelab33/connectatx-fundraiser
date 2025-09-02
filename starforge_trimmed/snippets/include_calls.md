Add these includes to your landing template (e.g., `app/templates/pages/home.html`) in this order:

```jinja
{% include 'components/hero_card.html' %}
{% include 'components/tiers_grid.html' %}
{% include 'components/impact_grid.html' %}
{% include 'components/header_about.html' %}
{% include 'components/footer_min.html' %}
```

Ensure `starforge.min.css` is linked in your base layout `<head>`:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/starforge.min.css') }}">
```

# app/routes/routes.py
# Back-compat shim: expose the admin blueprint as "bp" if something imports this module.
from .admin import admin_bp as bp  # noqa: F401

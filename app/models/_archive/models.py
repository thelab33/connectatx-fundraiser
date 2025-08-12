# app/auth.py
from __future__ import annotations

from typing import Optional

from flask import Flask, flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.wrappers.response import Response as WsgiResponse

from app.extensions import login_manager, db  # db optional if you want session.get
from app.models import User


def _load_user_by_id(user_id: str) -> Optional[User]:
    """Best-effort user lookup with guardrails."""
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return None

    # Prefer SQLAlchemy 2.x style if available
    try:
        # Flask-SQLAlchemy v3 exposes db.session.get
        return db.session.get(User, uid)  # type: ignore[arg-type]
    except Exception:
        # Fallback to classic query.get for older stacks
        try:
            return User.query.get(uid)  # type: ignore[attr-defined]
        except Exception:
            return None


def init_login(app: Flask) -> None:
    """
    Wire up Flask-Login pieces. Call from create_app().
    """
    login_manager.init_app(app)
    # Set your login view (adjust to your route)
    login_manager.login_view = "admin.dashboard"
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def _user_loader(user_id: str) -> Optional[User]:
        return _load_user_by_id(user_id)

    @login_manager.unauthorized_handler
    def _unauthorized() -> WsgiResponse | str:
        # If it's an API request, you might want JSON; here we keep it simple.
        flash("Please sign in to continue.", "warning")
        next_url = request.full_path if request.query_string else request.path
        try:
            return redirect(url_for(login_manager.login_view, next=next_url))
        except Exception:
            # If the login view isn’t registered yet, just go home.
            return redirect(url_for("main.home"))

    @app.context_processor
    def _inject_user():
        # Makes `current_user` available in all templates explicitly (Jinja already
        # exposes it via flask-login, but this keeps it predictable & testable).
        return dict(current_user=current_user)


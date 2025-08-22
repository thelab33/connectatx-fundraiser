from flask import current_app
from flask_login import current_user
from app.models import User
from app.extensions import login_manager

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    """
    Loads the user by their ID.
    This method is used by Flask-Login to retrieve the User object for the logged-in user.
    """
    return User.query.get(int(user_id))


# --- Context Processor for User ---
@current_app.context_processor
def inject_user():
    """
    Injects the current user into the template context.
    This allows access to the current user inside templates using `current_user`.
    """
    return dict(current_user=current_user)


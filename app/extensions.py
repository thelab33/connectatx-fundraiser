from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
import logging
from threading import Thread

# Initialize the Flask extensions as singletons for app-wide usage
db = SQLAlchemy()             # Database ORM
migrate = Migrate()           # Database migrations handler
socketio = SocketIO(cors_allowed_origins="*")  # SocketIO with open CORS for real-time websockets
cors = CORS()                 # Cross-Origin Resource Sharing for API calls
login_manager = LoginManager()  # User session/authentication manager
mail = Mail()                 # SMTP mail sender
babel = Babel()               # Internationalization and localization

# Configure Flask-Login
login_manager.login_view = "auth.login"  # Redirect unauthorized users to the login page
login_manager.session_protection = "strong"  # Adds extra session security

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """
    Given a user_id, load the corresponding User model instance.
    """
    from app.models import User
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logging.error(f"Error loading user {user_id}: {e}")
        return None


# Optional: Async email sending helper (can be upgraded to use Celery or Flask-Executor)
def send_email_async(app, msg):
    """
    Send emails asynchronously to avoid blocking the main thread.
    """
    def send(msg):
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                logging.error(f"Failed to send email: {e}")

    Thread(target=send, args=(msg,)).start()


import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_only_change_me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(os.getcwd(), "app/data/app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Basic CSP (headers usually set in app/__init__.py)
    CSP = {
        "default-src": "'self'",
        "script-src": "'self' 'nonce-{NONCE}' https://js.stripe.com",
        "connect-src": "'self' https://api.stripe.com https://m.stripe.network",
        "frame-src": "https://js.stripe.com https://hooks.stripe.com",
        "img-src": "'self' data: https://q.stripe.com",
        "style-src": "'self' 'unsafe-inline'",  # Tailwind inlined; adjust if using hash/nonce
    }


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    ENV = "production"

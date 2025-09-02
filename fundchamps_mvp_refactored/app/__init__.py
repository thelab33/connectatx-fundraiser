from flask import Flask, render_template
import os

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.getenv("SECRET_KEY", "change-me")

    @app.route("/")
    def home():
        return render_template("layouts/base.html", title="FundChamps")

    return app

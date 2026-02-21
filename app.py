from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from dotenv import load_dotenv
import os
import secrets
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder="Templates")
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_hex(32)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def sample_notifications():
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    return [
        {"time": now, "icon": "person-fill-check",        "color": "success", "detail": "Known face detected: Jamieson"},
        {"time": now, "icon": "box-seam",                 "color": "info",    "detail": "Package from AcmeCorp detected (front porch)"},
        {"time": now, "icon": "person-fill-exclamation",  "color": "warning", "detail": "Unknown person at the door"},
    ]


# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET"])
def login_page():
    if session.get("user"):
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    username_ok = secrets.compare_digest(username, ADMIN_USERNAME)
    password_ok = secrets.compare_digest(password, ADMIN_PASSWORD)
    if username_ok and password_ok:
        session["user"] = username
        return redirect(url_for("home"))
    flash("Invalid username or password.", "danger")
    return redirect(url_for("login_page"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── Protected routes ───────────────────────────────────────────────────────────

@app.route("/")
@login_required
def home():
    return render_template("index.html", user=session["user"], notifications=sample_notifications())


@app.route("/about")
@login_required
def about():
    return render_template("about.html", user=session["user"])


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

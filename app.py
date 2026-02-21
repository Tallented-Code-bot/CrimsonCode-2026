from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from dotenv import load_dotenv
import os
import secrets
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="Templates")
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_hex(32)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

# Decorator to require login for protected routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# Sample notifications for demonstration purposes
def sample_notifications():
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    return [
        {"time": now, "icon": "person-fill-check",        "color": "success", "detail": "Known face detected: Jamieson"},
        {"time": now, "icon": "box-seam",                 "color": "info",    "detail": "Package from AcmeCorp detected (front porch)"},
        {"time": now, "icon": "person-fill-exclamation",  "color": "warning", "detail": "Unknown person at the door"},
    ]


# ── Auth routes ────────────────────────────────────────────────────────────────

# Login page route to display the login form
@app.route("/login", methods=["GET"])
def login_page():
    if session.get("user"):
        return redirect(url_for("home"))
    return render_template("login.html")

# Login route to handle POST requests from the login form
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip() # Strip whitespace from username input
    password = request.form.get("password", "")

    # Basic login validation for demonstration purposes (use a proper authentication system in production)
    username_ok = secrets.compare_digest(username, ADMIN_USERNAME)
    password_ok = secrets.compare_digest(password, ADMIN_PASSWORD)

    # if both username and password are correct, set the session and redirect to home
    if username_ok and password_ok:
        session["user"] = username
        return redirect(url_for("home"))
    
    # if either is incorrect, flash an error message and redirect back to the login page
    flash("Invalid username or password.", "danger")
    return redirect(url_for("login_page"))

# Logout route to clear the session and redirect to login page
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── Protected routes ───────────────────────────────────────────────────────────

# Home page route, protected by login_required decorator
@app.route("/")
@login_required
def home():
    return render_template("index.html", user=session["user"], notifications=sample_notifications())

# About page route, also protected by login_required decorator
@app.route("/about")
@login_required
def about():
    return render_template("about.html", user=session["user"])


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

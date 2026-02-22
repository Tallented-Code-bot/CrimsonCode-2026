from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from services.db import get_admin, get_recent_events
import os
import secrets

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_hex(32)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def events_as_notifications():
    """Convert DB event rows into the dict format the template expects."""
    rows = get_recent_events(limit=20)
    notifications = []
    for row in rows:
        known = row["person_name"] != "Unknown"
        notifications.append({
            "time":   row["timestamp"],
            "icon":   "person-fill-check" if known else "person-fill-exclamation",
            "color":  "success"           if known else "warning",
            "detail": f"Known face detected: {row['person_name']}" if known
                      else "Unknown person detected",
        })
    return notifications


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
    admin = get_admin(username)
    if admin and check_password_hash(admin["password_hash"], password):
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
    return render_template("index.html", user=session["user"], notifications=events_as_notifications())


@app.route("/about")
@login_required
def about():
    return render_template("about.html", user=session["user"])


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

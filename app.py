import os
import secrets
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from services.db import get_admin, get_events_since, get_recent_events
from services.detector import start as start_detector

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_hex(32)


# Decorator to require login for protected routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)

    return decorated


def _row_to_notification(row):
    event_type = row["event_type"]
    if event_type == "entered":
        icon, color = "person-plus-fill", "success"
    elif event_type == "left":
        icon, color = "person-dash-fill", "warning"
    else:
        icon, color = "person-fill-exclamation", "secondary"
    return {
        "id": row["id"],
        "time": row["timestamp"],
        "icon": icon,
        "color": color,
        "detail": row["person_name"],
    }


def events_as_notifications():
    """Convert DB event rows into the dict format the template expects."""
    return [_row_to_notification(r) for r in get_recent_events(limit=20)]


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
    username = request.form.get(
        "username", ""
    ).strip()  # Strip whitespace from username input
    password = request.form.get("password", "")
    admin = get_admin(username)
    if admin and check_password_hash(admin["password_hash"], password):
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
    return render_template(
        "index.html", user=session["user"], notifications=events_as_notifications()
    )


# About page route, also protected by login_required decorator
@app.route("/about")
@login_required
def about():
    return render_template("about.html", user=session["user"])


# ── API ────────────────────────────────────────────────────────────────────────


@app.route("/api/events")
def api_events():
    if not session.get("user"):
        return jsonify([]), 401
    since_id = request.args.get("since", 0, type=int)
    rows = get_events_since(since_id)
    return jsonify([_row_to_notification(r) for r in rows])


# ── Start detector (runs regardless of how Flask is launched) ──────────────────

_stream_url = os.getenv("STREAM_URL", "https://www.youtube.com/watch?v=UUhTr19MH0k")
start_detector(_stream_url)


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

# ...existing code...
from flask import Flask, render_template, request, redirect, session, url_for
import os
import json
import secrets
from datetime import datetime

# Use the provided Templates folder (capitalized in your project)
app = Flask(__name__, template_folder="Templates")
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_hex(16)

# BASIC USER MANAGEMENT USING A JSON FILE (FOR SIMPLICITY, NOT SECURE, NO HASHING)
BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# LOAD USERS FROM A USER FILE (FOR SIMPLICITY, NOT SECURE, NO HASHING)
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# SAVE USERS TO A USER FILE (FOR SIMPLICITY, NOT SECURE, NO HASHING)
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# NOTIFICATION SAMPLE FUNCTION
def sample_notifications(username):
    # Minimal, deterministic sample notifications related to README (faces/brands)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return [
        {"time": now, "type": "face", "detail": "Known face detected: Jamieson"},
        {"time": now, "type": "brand", "detail": "Package from AcmeCorp detected (front porch)"},
        {"time": now, "type": "unknown", "detail": "Unknown person at the door"},
    ]

# Root location
@app.route('/')
def root():
    return redirect(url_for('login_page'))

# LOGIN PAGE ROUTE
@app.route('/login-page')
def login_page():
    return render_template("login.html")

# HOME PAGE ROUTE
@app.route('/home')
def home():
    user = session.get("user")
    notifications = sample_notifications(user) if user else []
    return render_template("index.html", user=user, notifications=notifications)

@app.route('/about')
def about():
    return render_template("about.html")


# SIGNUP ROUTE
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        return redirect(url_for('home'))
    users = load_users()
    if username in users:
        return redirect(url_for('home'))
    users[username] = {"password": password}
    save_users(users)
    session['user'] = username
    return redirect(url_for('home'))


# LOGIN ROUTE
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    users = load_users()
    if username and username in users and users[username].get('password') == password:
        session['user'] = username
        return redirect(url_for('home'))
    return redirect(url_for('home'))

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# MAIN CODE HERE
if __name__ == '__main__':
    app.run(debug=True)
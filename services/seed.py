"""
Run once to initialise the database and create default data.

Reads ADMIN_USERNAME and ADMIN_PASSWORD from .env if present.
"""
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from .db import init_db, get_db

_ROOT = os.path.join(os.path.dirname(__file__), "..")
load_dotenv(os.path.join(_ROOT, ".env"))

# Names of the three group members the face model will recognise.
KNOWN_PERSONS = [
    "Person 1",
    "Person 2",
    "Person 3",
]


def seed(admin_username: str = None, admin_password: str = None):
    admin_username = admin_username or os.getenv("ADMIN_USERNAME", "admin")
    admin_password = admin_password or os.getenv("ADMIN_PASSWORD", "changeme")
    init_db()

    with get_db() as db:
        # Admin account
        db.execute(
            "INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)",
            (admin_username, generate_password_hash(admin_password)),
        )

        # Known persons (face labels for the custom classifier)
        for name in KNOWN_PERSONS:
            db.execute(
                "INSERT OR IGNORE INTO persons (name) VALUES (?)", (name,)
            )

    print("Database initialised.")
    print(f"  Admin username : {admin_username}")
    print(f"  Admin password : {admin_password}")
    print(f"  Known persons  : {', '.join(KNOWN_PERSONS)}")


if __name__ == "__main__":
    seed()

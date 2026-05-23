import sqlite3
import bcrypt
from pathlib import Path

# ======================================
# DATABASE PATH
# ======================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = BASE_DIR / "users.db"

# ======================================
# CREATE USERS TABLE
# ======================================

def create_users_table():

    conn = sqlite3.connect(str(DB_NAME))
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password BLOB
    )
    """)

    conn.commit()
    conn.close()

# ======================================
# REGISTER USER
# ======================================

def register_user(name, email, password):

    conn = sqlite3.connect(str(DB_NAME))
    c = conn.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        c.execute(
            """
            INSERT INTO users (
                name,
                email,
                password
            )
            VALUES (?,?,?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()

# ======================================
# LOGIN USER
# ======================================

def login_user(email, password):

    conn = sqlite3.connect(str(DB_NAME))
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = c.fetchone()

    conn.close()

    if user:

        stored_password = user[3]

        if bcrypt.checkpw(
            password.encode(),
            stored_password
        ):

            return user

    return None
import sqlite3
from pathlib import Path

DB_PATH = "data/assistiq.db"

Path("data").mkdir(exist_ok=True)


def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_connection()

    # USERS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # CONVERSATIONS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title TEXT
    )
    """)

    # MESSAGES
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        role TEXT,
        content TEXT
    )
    """)

    conn.commit()

    conn.close()


# ==========================
# CONVERSATION FUNCTIONS
# ==========================

def create_conversation(username, title):

    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO conversations(username, title)
        VALUES(?,?)
        """,
        (username, title)
    )

    conn.commit()

    conversation_id = cursor.lastrowid

    conn.close()

    return conversation_id


def get_conversations(username):

    conn = get_connection()

    conversations = conn.execute(
        """
        SELECT * FROM conversations
        WHERE username=?
        ORDER BY id DESC
        """,
        (username,)
    ).fetchall()

    conn.close()

    return conversations


# ==========================
# MESSAGE FUNCTIONS
# ==========================

def save_message(conversation_id, role, content):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO messages(conversation_id, role, content)
        VALUES(?,?,?)
        """,
        (conversation_id, role, content)
    )

    conn.commit()

    conn.close()


def get_messages(conversation_id):

    conn = get_connection()

    messages = conn.execute(
        """
        SELECT * FROM messages
        WHERE conversation_id=?
        """,
        (conversation_id,)
    ).fetchall()

    conn.close()

    return messages
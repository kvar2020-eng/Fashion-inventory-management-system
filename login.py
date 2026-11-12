"""User registration and login with salted PBKDF2 password hashes."""
import hashlib
import hmac
import os
from database import connect_db

_ITERATIONS = 310_000

def _hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return salt.hex() + "$" + digest.hex()

def _verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        candidate = _hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return hmac.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError):
        return False

def signup_user(username, password):
    username = username.strip()
    if not username or not password:
        raise ValueError("Username and password are required.")
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password_hash) VALUES (%s,%s)",
                    (username, _hash_password(password)))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def login_user(username, password):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username=%s", (username.strip(),))
        row = cur.fetchone()
        return bool(row and _verify_password(password, row[0]))
    finally:
        conn.close()

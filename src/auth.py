import sqlite3
import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def create_user(username, password, email, user_type, address=None, customer_type=None):
    if not username or not password or not email:
        print("Username, password, and email are required.")
        return None

    if not is_valid_email(email):
        print("Invalid email.")
        return None

    if customer_type not in (None, 'individual', 'retail'):
        print("Invalid customer type.")
        return None

    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()

    try:
        c.execute('''INSERT INTO users
                     (username, password_hash, email, user_type, address, customer_type)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (username.strip(), hash_password(password), email.strip(), user_type.strip(),
                   address.strip() if address else None,
                   customer_type.strip() if customer_type else None))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_user(username, password):
    if not username or not password:
        print("Username and password are required.")
        return None

    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()

    c.execute('''SELECT id, password_hash, user_type FROM users WHERE username = ?''', (username,))
    result = c.fetchone()
    conn.close()

    if result and result[1] == hash_password(password):
        return (result[0], result[2])
    return None
import pytest
from src.auth import hash_password, is_valid_email, create_user, authenticate_user
import sqlite3

@pytest.fixture
def setup_database():
    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT UNIQUE,
                    user_type TEXT,
                    address TEXT,
                    customer_type TEXT
                )''')
    conn.commit()
    yield
    conn.close()

@pytest.fixture
def clear_database():
    yield
    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()
    c.execute('DELETE FROM users')
    conn.commit()
    conn.close()

def test_hash_password():
    assert hash_password("password123") == hash_password("password123")
    assert hash_password("password123") != hash_password("differentpassword")

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("another@domain.org", True),
    ("missing@dot", False)
])
def test_is_valid_email(email, expected):
    assert is_valid_email(email) == expected

def test_create_user_valid(setup_database, clear_database):
    user_id = create_user("testuser", "password123", "testuser@example.com", "customer", "123 Street", "individual")
    assert user_id is not None

@pytest.mark.parametrize("username,password,email,user_type,address,customer_type", [
    ("", "password123", "testuser@example.com", "customer", "123 Street", "individual"),
    ("testuser", "", "testuser@example.com", "customer", "123 Street", "individual"),
    ("testuser", "password123", "", "customer", "123 Street", "individual"),
    ("testuser", "password123", "bademail", "customer", "123 Street", "individual"),
    ("testuser", "password123", "testuser@example.com", "customer", "123 Street", "wrongtype")
])
def test_create_user_invalid(setup_database, clear_database, username, password, email, user_type, address, customer_type):
    user_id = create_user(username, password, email, user_type, address, customer_type)
    assert user_id is None

def test_authenticate_user_success(setup_database, clear_database):
    create_user("authuser", "securepassword", "authuser@example.com", "customer")
    user = authenticate_user("authuser", "securepassword")
    assert user is not None
    assert user[1] == "customer"

@pytest.mark.parametrize("username,password", [
    ("wronguser", "securepassword"),
    ("authuser", "wrongpassword"),
    ("", "securepassword"),
    ("authuser", "")
])
def test_authenticate_user_failure(setup_database, clear_database, username, password):
    create_user("authuser", "securepassword", "authuser@example.com", "customer")
    user = authenticate_user(username, password)
    assert user is None

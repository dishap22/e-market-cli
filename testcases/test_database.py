import sqlite3
import os
import pytest
from src.database import initialize_database

@pytest.fixture
def setup_and_teardown_db():
    if os.path.exists('emarket.db'):
        os.remove('emarket.db')

    initialize_database()

    yield

    if os.path.exists('emarket.db'):
        os.remove('emarket.db')


def test_database_creation(setup_and_teardown_db):
    assert os.path.exists('emarket.db')

    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    expected_tables = ['users', 'products', 'orders', 'coupons']

    for table in expected_tables:
        assert table in tables, f"Table '{table}' was not created!"

    conn.close()


def test_table_columns(setup_and_teardown_db):
    """ Ensure key tables have the correct columns. """
    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()

    c.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in c.fetchall()]
    assert user_columns == ['id', 'username', 'password_hash', 'email', 'user_type', 'address', 'customer_type']

    c.execute("PRAGMA table_info(products)")
    product_columns = [col[1] for col in c.fetchall()]
    assert product_columns == ['id', 'name', 'price', 'category', 'seller_id']

    conn.close()


def test_id_autoincrement(setup_and_teardown_db):
    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash, email, user_type) VALUES (?, ?, ?, ?)",
              ('testuser', 'hashedpassword', 'test@example.com', 'customer'))
    conn.commit()

    c.execute("SELECT id FROM users WHERE username = ?", ('testuser',))
    user_id = c.fetchone()[0]
    assert user_id == 1, "User ID should start from 1 and auto-increment!"

    conn.close()

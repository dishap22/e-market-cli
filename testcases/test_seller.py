import pytest
from src.seller import Seller
import sqlite3

@pytest.fixture
def setup_seller():
    seller = Seller(1, "test_seller", "seller@example.com")
    seller.conn = sqlite3.connect(':memory:')
    c = seller.conn.cursor()
    c.execute('''CREATE TABLE products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  price REAL,
                  category TEXT,
                  seller_id INTEGER)''')
    seller.conn.commit()
    return seller

def test_seller_init(setup_seller):
    seller = setup_seller
    assert seller.id == 1
    assert seller.username == "test_seller"
    assert seller.email == "seller@example.com"
    assert seller.type == "seller"
    assert seller.products == []

def test_add_product(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("Test Product", 10.99, "Electronics")

    assert product_id is not None
    c = seller.conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()

    assert product is not None
    assert product[1] == "Test Product"
    assert product[2] == 10.99
    assert product[3] == "Electronics"
    assert product[4] == seller.id

def test_add_product_invalid_price(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("Invalid Price Product", -5, "Misc")
    assert product_id is None

def test_add_product_empty_name(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("", 10, "Category")
    assert product_id is None

def test_add_product_no_category(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("Product No Category", 15.99, "")
    assert product_id is None

def test_add_product_whitespace_name(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("   ", 12.99, "Misc")
    assert product_id is None

def test_add_product_whitespace_category(setup_seller):
    seller = setup_seller
    product_id = seller.add_product("Valid Product", 12.99, "   ")
    assert product_id is None
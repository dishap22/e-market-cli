import pytest
from src.system import EMarketSystem
from src.user import Customer, Seller
from src.discount_coupon import DiscountCoupon
import sqlite3

@pytest.fixture
def setup_system():
    system = EMarketSystem()
    system.conn = sqlite3.connect(':memory:')
    c = system.conn.cursor()

    c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      email TEXT,
                      user_type TEXT,
                      address TEXT,
                      customer_type TEXT)''')

    c.execute('''CREATE TABLE products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      price REAL,
                      category TEXT,
                      seller_id INTEGER,
                      FOREIGN KEY(seller_id) REFERENCES users(id))''')

    c.execute('''CREATE TABLE orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer_id INTEGER,
                      product_id INTEGER,
                      seller_id INTEGER,
                      price REAL,
                      order_date DATETIME,
                      delivery_status TEXT DEFAULT 'Processing',
                      tracking_number TEXT,
                      FOREIGN KEY(customer_id) REFERENCES users(id),
                      FOREIGN KEY(product_id) REFERENCES products(id),
                      FOREIGN KEY(seller_id) REFERENCES users(id))''')

    c.execute('''CREATE TABLE coupons
                     (code TEXT PRIMARY KEY,
                      customer_id INTEGER,
                      discount REAL,
                      expiry DATETIME,
                      FOREIGN KEY(customer_id) REFERENCES users(id))''')


    system.conn.commit()
    return system

def test_get_user(setup_system):
    system = setup_system
    c = system.conn.cursor()
    c.execute("""INSERT INTO users (id, username, email, user_type) VALUES (1, 'John Doe', 'john@example.com', 'customer')""")
    system.conn.commit()
    user = system.get_user(1)
    assert user is not None
    assert user.username == 'John Doe'
    assert user.email == 'john@example.com'

def test_search_products(setup_system):
    system = setup_system
    c = system.conn.cursor()
    c.execute("""INSERT INTO products (name, price, category, seller_id) VALUES ('Phone', 999.99, 'Electronics', 1)""")
    system.conn.commit()
    products = system.search_products('Phone')
    assert len(products) == 1
    assert products[0][1] == 'Phone'

def test_add_product_as_seller(setup_system):
    system = setup_system
    system.current_user = Seller(1, 'Seller1', 'seller@example.com')
    product_id = system.add_product('Laptop', 1299.99, 'Electronics')
    assert product_id is not None

def test_add_product_as_customer(setup_system):
    system = setup_system
    system.current_user = Customer(1, 'Customer1', 'customer@example.com', '123 Street', '1234567890')
    assert not system.add_product('Laptop', 1299.99, 'Electronics')

def test_checkout(setup_system):
    system = setup_system
    system.current_user = Customer(1, 'Customer1', 'customer@example.com', '123 Street', '1234567890')
    system.current_user.cart = [{'product_id': 1, 'price': 100.0}]
    c = system.conn.cursor()
    c.execute("""INSERT INTO products (id, name, price, category, seller_id) VALUES (1, 'Item1', 100.0, 'General', 1)""")
    system.conn.commit()
    assert system.checkout() == True

def test_checkout_no_items(setup_system):
    system = setup_system
    system.current_user = Customer(1, 'Customer1', 'customer@example.com', '123 Street', '1234567890')
    system.current_user.cart = []
    assert not system.checkout()

def test_generate_coupon(setup_system):
    system = setup_system
    system.generate_coupon(1)
    c = system.conn.cursor()
    c.execute("SELECT * FROM coupons WHERE customer_id = ?", (1,))
    coupon = c.fetchone()
    assert coupon is not None

def test_get_best_valid_coupon(setup_system):
    system = setup_system
    system.generate_coupon(1)
    coupon = system.get_best_valid_coupon(1)
    assert coupon is not None
    assert isinstance(coupon, DiscountCoupon)

def test_get_orders_for_customer(setup_system):
    system = setup_system
    c = system.conn.cursor()
    c.execute("""INSERT INTO orders (customer_id, product_id, seller_id, price, order_date) VALUES (1, 1, 2, 50.0, '2024-01-01')""")
    system.conn.commit()
    orders = system.get_orders_for_customer(1)
    assert len(orders) == 1

def test_get_orders_for_seller(setup_system):
    system = setup_system
    c = system.conn.cursor()
    c.execute("""INSERT INTO orders (customer_id, product_id, seller_id, price, order_date) VALUES (1, 1, 2, 50.0, '2024-01-01')""")
    system.conn.commit()
    orders = system.get_orders_for_seller(2)
    assert len(orders) == 1

def test_update_delivery_status(setup_system):
    system = setup_system
    c = system.conn.cursor()
    c.execute("""INSERT INTO orders (id, customer_id, product_id, seller_id, price, order_date, delivery_status) VALUES (1, 1, 1, 2, 50.0, '2024-01-01', 'Processing')""")
    system.conn.commit()
    system.update_delivery_status(1, 'Shipped', 'TRACK123')
    c.execute("SELECT delivery_status, tracking_number FROM orders WHERE id = 1")
    status = c.fetchone()
    assert status[0] == 'Shipped'
    assert status[1] == 'TRACK123'

import sqlite3
import os

def initialize_database():
    db_exists = os.path.exists('emarket.db')

    conn = sqlite3.connect('emarket.db')
    c = conn.cursor()

    if not db_exists:
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

        conn.commit()
        print("Database tables created successfully!")
    conn.close()

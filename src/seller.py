from src.user import User
from src.product import Product

class Seller(User):
    def __init__(self, id, name, email):
        super().__init__(id, name, email, 'seller')
        self.products = []

    def add_product(self, name, price, category):
        c = self.conn.cursor()
        c.execute('''INSERT INTO products (name, price, category, seller_id)
                     VALUES (?, ?, ?, ?)''',
                  (name, price, category, self.id))
        self.conn.commit()
        return c.lastrowid
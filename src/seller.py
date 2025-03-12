from src.user import User

class Seller(User):
    def __init__(self, id, name, email):
        super().__init__(id, name, email, 'seller')
        self.products = []

    def add_product(self, name, price, category):
        if not name.strip():
            print("Error adding product: Product name cannot be empty!")
            return None

        if price <= 0:
            print("Error adding product: Price must be greater than 0!")
            return None

        if not category.strip():
            print("Error adding product: Category cannot be empty!")
            return None

        c = self.conn.cursor()
        c.execute('''INSERT INTO products (name, price, category, seller_id)
                     VALUES (?, ?, ?, ?)''',
                  (name, price, category, self.id))
        self.conn.commit()
        return c.lastrowid
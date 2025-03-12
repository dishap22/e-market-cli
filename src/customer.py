from src.user import User
from src.product import Product

class Customer(User):
    def __init__(self, id, name, email, customer_type):
        super().__init__(id, name, email, 'customer')
        self.address = None
        self.customer_type = customer_type
        self.order_count = 0
        self.cart = []
        self.discount = 0.0 if customer_type == 'individual' else 0.1

    def set_address(self, address):
        self.address = address

    def add_to_cart(self, product: Product):
        self.cart.append({'product_id': product.id, 'price': product.price})
        print(f"Added {product.name} to cart.")
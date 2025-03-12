from datetime import datetime
from src.product import Product

class OrderItem:
    def __init__(self, product: Product, quantity):
        self.product = product
        self.quantity = quantity

class Order:
    def __init__(self, id, customer_id, total, items):
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.items = items
        self.date = datetime.now()

class Delivery:
    def __init__(self, order_id, address):
        self.order_id = order_id
        self.address = address
        self.status = "Processing"

    def update_status(self, status):
        self.status = status
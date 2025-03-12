class User:
    def __init__(self, user_id, username, email, user_type):
        self.id = user_id
        self.username = username
        self.email = email
        self.type = user_type

class Customer(User):
    def __init__(self, user_id, username, email, address, customer_type):
        super().__init__(user_id, username, email, 'customer')
        self.address = address
        self.customer_type = customer_type
        self.cart = []

class Seller(User):
    def __init__(self, user_id, username, email):
        super().__init__(user_id, username, email, 'seller')
class DiscountCoupon:
    def __init__(self, code, customer_id, discount, expiry):
        self.code = code
        self.customer_id = customer_id
        self.discount = discount
        self.expiry = expiry
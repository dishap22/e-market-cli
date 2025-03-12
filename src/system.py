import sqlite3
from datetime import datetime, timedelta
from src.user import Customer, Seller
from src.discount_coupon import DiscountCoupon
import random
import string

class EMarketSystem:
    def __init__(self):
        self.conn = sqlite3.connect('emarket.db')
        self.current_user = None

    def get_user(self, user_id):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM users WHERE id = ?''', (user_id,))
        user_data = c.fetchone()

        if not user_data:
            return None

        if user_data[4] == 'customer':
            return Customer(user_data[0], user_data[1], user_data[3],
                           user_data[5], user_data[6])
        else:
            return Seller(user_data[0], user_data[1], user_data[3])

    def search_products(self, keyword):
        c = self.conn.cursor()
        c.execute('''SELECT id, name, price, category FROM products
                     WHERE name LIKE ? OR category LIKE ?''',
                  (f'%{keyword}%', f'%{keyword}%'))
        return c.fetchall()

    def add_product(self, name, price, category):
        if not isinstance(self.current_user, Seller):
            return False

        c = self.conn.cursor()
        c.execute('''INSERT INTO products
                     (name, price, category, seller_id)
                     VALUES (?, ?, ?, ?)''',
                  (name, price, category, self.current_user.id))
        self.conn.commit()
        return c.lastrowid

    def checkout(self):
        if not isinstance(self.current_user, Customer) or not self.current_user.cart:
            return False

        try:
            c = self.conn.cursor()

            total = sum(item['price'] for item in self.current_user.cart)
            order_count = len(self.current_user.cart)

            discount_applied = False
            if order_count > 10:
                total *= 0.9
                discount_applied = True
                discount_amount = 0.1
                print(f"Applied 10% bulk discount on your total order of ${total:.2f}!")

            best_coupon = self.get_best_valid_coupon(self.current_user.id)
            coupon_discount = 0
            if best_coupon:
                coupon_discount = best_coupon.discount
                if not discount_applied or coupon_discount > 0.1:
                    total *= (1 - coupon_discount)
                    discount_applied = True
                    discount_amount = coupon_discount
                    print(f"Applied {best_coupon.code} coupon for {coupon_discount*100}% discount!")

            order_ids = []
            for item in self.current_user.cart:
                product_id = item['product_id']

                c.execute('''SELECT id, price, seller_id FROM products WHERE id = ?''', (product_id,))
                product_data = c.fetchone()

                if not product_data:
                    print(f"Product {product_id} is no longer available.")
                    continue

                item_price = product_data[1]
                if discount_applied:
                    item_price *= (1 - discount_amount)

                c.execute('''INSERT INTO orders
                           (customer_id, product_id, seller_id, price, order_date)
                           VALUES (?, ?, ?, ?, ?)''',
                        (self.current_user.id, product_id, product_data[2],
                         item_price, datetime.now()))

                order_ids.append(c.lastrowid)

                c.execute('''DELETE FROM products WHERE id = ?''', (product_id,))

            if not order_ids:
                print("No valid products to checkout.")
                self.conn.rollback()
                return False

            self.conn.commit()
            self.current_user.cart = []

            print(f"\nCheckout completed successfully!")
            if discount_applied:
                print(f"Discount applied: {discount_amount*100}%")
                print(f"Final total: ${total:.2f}")
            print(f"Created {len(order_ids)} order(s)")

            c.execute('''SELECT COUNT(*) FROM orders WHERE customer_id = ?''', (self.current_user.id,))
            order_count = c.fetchone()[0]

            if order_count % 5 == 0:
                self.generate_coupon(self.current_user.id)


            return True
        except Exception as e:
            print(f"Error during checkout: {e}")
            self.conn.rollback()
            return False

    def generate_coupon(self, customer_id):
        coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expiry_date = datetime.now() + timedelta(days=30)
        c = self.conn.cursor()
        c.execute('''INSERT INTO coupons (code, customer_id, discount, expiry)
                     VALUES (?, ?, ?, ?)''', (coupon_code, customer_id, 0.15, expiry_date))
        self.conn.commit()
        print(f"Congrats! You've earned a 15% discount coupon for your next order: {coupon_code}")

    def get_best_valid_coupon(self, customer_id):
        c = self.conn.cursor()
        c.execute('''SELECT code, customer_id, discount, expiry FROM coupons
                    WHERE customer_id = ? AND expiry > ?
                    ORDER BY discount DESC
                    LIMIT 1''',
                (customer_id, datetime.now()))
        coupon_data = c.fetchone()

        if coupon_data:
            return DiscountCoupon(coupon_data[0], coupon_data[1], coupon_data[2], coupon_data[3])
        return None

    def get_orders_for_customer(self, customer_id):
        c = self.conn.cursor()
        c.execute('''SELECT id, price, order_date, delivery_status, tracking_number, product_id
                     FROM orders
                     WHERE customer_id = ?''', (customer_id,))
        return c.fetchall()

    def get_orders_for_seller(self, seller_id):
        c = self.conn.cursor()
        c.execute('''SELECT id, customer_id, price, order_date, delivery_status, tracking_number, product_id
                     FROM orders
                     WHERE seller_id = ?''', (seller_id,))
        return c.fetchall()

    def update_delivery_status(self, order_id, status, tracking_number=None):
        c = self.conn.cursor()
        c.execute('''UPDATE orders
                     SET delivery_status = ?, tracking_number = ?
                     WHERE id = ?''', (status, tracking_number, order_id))
        self.conn.commit()
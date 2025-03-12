from src.system import EMarketSystem
import src.auth as auth
from src.database import initialize_database

def main():
    system = EMarketSystem()

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose option: ")

        if choice == '3':
            break

        elif choice == '1':
            user_type = input("User type (customer/seller): ")
            username = input("Username: ")
            password = input("Password: ")
            email = input("Email: ")

            if user_type == 'customer':
                address = input("Address: ")
                customer_type = input("Customer type (individual/retail): ")
                user_id = auth.create_user(username, password, email, 'customer',
                                          address, customer_type)
            else:
                user_id = auth.create_user(username, password, email, 'seller')

            if user_id:
                print(f"Registered successfully! ID: {user_id}")
            else:
                print("Registration failed (username might be taken)")

        elif choice == '2':
            username = input("Username: ")
            password = input("Password: ")
            auth_result = auth.authenticate_user(username, password)

            if auth_result:
                user_id, user_type = auth_result
                user = system.get_user(user_id)

                if not user:
                    print("User not found")
                    continue

                system.current_user = user
                print(f"Welcome {system.current_user.username}!")

                if user_type == 'customer':
                    handle_customer(system)
                else:
                    handle_seller(system)
            else:
                print("Invalid credentials")

def handle_customer(system):
    while True:
        print("\n1. Search Products\n2. View Cart\n3. Checkout\n4. View Orders\n5. Logout")
        choice = input("Choose option: ")

        if choice == '5':
            break

        elif choice == '1':
            keyword = input("Search term: ")
            products = system.search_products(keyword)

            if not products:
                print("No products found.")
                continue

            for p in products:
                print(f"{p[0]}: {p[1]} (${p[2]}) - Category: {p[3]}")

            pid = input("Enter product ID to add to cart (0 to cancel): ")
            if pid.isdigit() and int(pid) > 0:
                pid = int(pid)
            # Find the product in the search results
            matching_products = [p for p in products if p[0] == pid]
            if matching_products:
                product = matching_products[0]
                system.current_user.cart.append({
                    'product_id': pid,
                    'price': product[2]
                })
                print(f"Added {product[1]} to cart!")
            else:
                print(f"Product with ID {pid} not found in search results.")

        elif choice == '2':
            print("\nCart:")
            total = 0
            for i, item in enumerate(system.current_user.cart):
                c = system.conn.cursor()
                c.execute("SELECT name FROM products WHERE id = ?", (item['product_id'],))
                product_name = c.fetchone()
                if product_name:
                    print(f"{i+1}. {product_name[0]} - ${item['price']:.2f}")
                    total += item['price']
                else:
                    print(f"{i+1}. Product {item['product_id']} (no longer available)")

            if not system.current_user.cart:
                print("Your cart is empty.")
            else:
                print(f"Total: ${total:.2f}")
                # Show discount preview
                if len(system.current_user.cart) > 10:
                    print(f"You qualify for a 10% bulk discount: ${total * 0.9:.2f}")

        elif choice == '3':
            if system.checkout():
                print("Order placed successfully!")
            else:
                print("Checkout failed")

        elif choice == '4':
            orders = system.get_orders_for_customer(system.current_user.id)
            if not orders:
                print("No orders found")
            else:
                total_spent = 0
                for order in orders:
                    c = system.conn.cursor()
                    c.execute("SELECT name FROM products WHERE id = ?", (order[5],))
                    product_name = c.fetchone()

                    print(f"\nOrder ID: {order[0]}")
                    print(f"Product: {product_name[0] if product_name else 'Unknown'}")
                    print(f"Price: ${order[1]:.2f}")
                    print(f"Order Date: {order[2]}")
                    print(f"Delivery Status: {order[3]}")
                    if order[4]:  # Tracking number
                        print(f"Tracking Number: {order[4]}")

                    total_spent += order[1]

                print(f"\nTotal spent: ${total_spent:.2f}")

def handle_seller(system):
    while True:
        print("\n1. Add Product\n2. View Products\n3. View Orders\n4. Update Order Status\n5. Logout")
        choice = input("Choose option: ")

        if choice == '5':
            break

        elif choice == '1':
            name = input("Product name: ")

            if not name.strip():
                print("Product name cannot be empty!")
                continue

            while True:
                try:
                    price = float(input("Price: "))
                    if price <= 0:
                        print("Price must be greater than 0!")
                    else:
                        break
                except ValueError:
                    print("Invalid price! Please enter a number.")

            category = input("Category: ")

            if not category.strip():
                print("Category cannot be empty!")
                continue

            pid = system.add_product(name, price, category)

            if pid:
                print(f"Product added! ID: {pid}")
            else:
                print("Failed to add product")

        elif choice == '2':
            c = system.conn.cursor()
            c.execute('''SELECT id, name, price, category FROM products
                         WHERE seller_id = ?''', (system.current_user.id,))
            products = c.fetchall()

            if not products:
                print("You haven't added any products yet.")
            else:
                for p in products:
                    print(f"{p[0]}: {p[1]} (${p[2]}) - Category: {p[3]}")

        elif choice == '3':
            orders = system.get_orders_for_seller(system.current_user.id)

            if not orders:
                print("No orders found")
            else:
                for order in orders:
                    c = system.conn.cursor()
                    c.execute("SELECT name FROM products WHERE id = ?", (order[6],))
                    product_name = c.fetchone()

                    print(f"\nOrder ID: {order[0]}")
                    print(f"Customer ID: {order[1]}")
                    print(f"Product: {product_name[0] if product_name else 'Unknown'}")
                    print(f"Price: ${order[2]:.2f}")
                    print(f"Order Date: {order[3]}")
                    print(f"Delivery Status: {order[4]}")
                    if order[5]:  # Tracking number
                        print(f"Tracking Number: {order[5]}")

        elif choice == '4':
            order_id = input("Enter order ID: ")
            if not order_id.isdigit():
                print("Invalid order ID")
                continue

            c = system.conn.cursor()
            c.execute('''SELECT id FROM orders
                        WHERE id = ? AND seller_id = ?''',
                    (order_id, system.current_user.id))
            if not c.fetchone():
                print("You are not the seller for this order")
                continue

            status = input("Enter new status (e.g., Shipped, Delivered): ")
            tracking_number = input("Enter tracking number (optional): ")
            system.update_delivery_status(int(order_id), status, tracking_number)
            print("Order status updated!")

if __name__ == "__main__":
    initialize_database()
    main()
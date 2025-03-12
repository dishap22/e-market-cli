import pytest
from src.customer import Customer
from src.product import Product

def test_customer_initialization():
    cust = Customer(1, "John Doe", "john@example.com", "individual")
    assert cust.username == "John Doe"
    assert cust.email == "john@example.com"
    assert cust.customer_type == "individual"
    assert cust.discount == 0.0

def test_customer_discount_retail():
    cust = Customer(2, "Retail Shop", "retail@example.com", "retail")
    assert cust.discount == 0.1

def test_set_address():
    cust = Customer(3, "Jane Doe", "jane@example.com", "individual")
    cust.set_address("123 Elm St")
    assert cust.address == "123 Elm St"

def test_add_to_cart():
    cust = Customer(4, "Mark", "mark@example.com", "individual")
    product = Product(101, "Laptop", 1000, "Electronics", 1)
    cust.add_to_cart(product)
    assert len(cust.cart) == 1
    assert cust.cart[0]['product_id'] == 101
    assert cust.cart[0]['price'] == 1000

def test_add_invalid_product():
    cust = Customer(5, "Invalid Test", "invalid@example.com", "individual")
    with pytest.raises(AttributeError):
        cust.add_to_cart(None)

import os
import psycopg2
import random
from datetime import date, timedelta

# Connect to PostgreSQL
connection = psycopg2.connect(
    host="localhost",
    database="revenue_intelligence",
    user="postgres",
    password=os.environ["0506"]
)

cursor = connection.cursor()

# -----------------------------
# Generate Customers
# -----------------------------

first_names = [
    "Rahul", "Ananya", "Arjun", "Priya", "Kiran",
    "Sneha", "Ravi", "Pooja", "Vikram", "Meena"
]

last_names = [
    "Kumar", "Sharma", "Reddy", "Patel", "Rao",
    "Singh", "Verma", "Nair", "Iyer", "Das"
]

cities = [
    "Bengaluru", "Hyderabad", "Chennai", "Mumbai",
    "Delhi", "Pune", "Kolkata", "Ahmedabad"
]

# Generate 500 customers
for i in range(500):

    name = random.choice(first_names) + " " + random.choice(last_names)
    email = f"customer{i + 1}@example.com"
    gender = random.choice(["Male", "Female"])
    age = random.randint(18, 55)
    city = random.choice(cities)

    registration_date = date(2025, 1, 1) + timedelta(
        days=random.randint(0, 600)
    )

    cursor.execute(
        """
        INSERT INTO customers
        (customer_name, email, gender, age, city, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (name, email, gender, age, city, registration_date)
    )

# -----------------------------
# Generate Products
# -----------------------------

categories = [
    "Electronics",
    "Footwear",
    "Clothing",
    "Accessories",
    "Home & Kitchen"
]

product_names = [
    "Wireless Earbuds",
    "Smart Watch",
    "Running Shoes",
    "Backpack",
    "Bluetooth Speaker",
    "Laptop Stand",
    "Travel Bag",
    "Fitness Band",
    "T-Shirt",
    "Water Bottle"
]

# Generate 100 products
for i in range(100):

    product_name = random.choice(product_names) + f" Model {i + 1}"
    category = random.choice(categories)

    price = round(random.uniform(500, 10000), 2)

    cost = round(price * random.uniform(0.45, 0.75), 2)

    stock_quantity = random.randint(20, 300)

    cursor.execute(
        """
        INSERT INTO products
        (product_name, category, price, cost, stock_quantity)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            product_name,
            category,
            price,
            cost,
            stock_quantity
        )
    )

# Save everything
connection.commit()

print("500 customers and 100 products generated successfully!")

cursor.close()
connection.close()



import sqlite3
import pickle
import os
from optparse import OptionParser

db_name = "inventory.db"
admin_user = "admin"
admin_pass = "password123"
current_user = ""
LOW_STOCK = 5
conn = None
cursor = None

print("=" * 50)
print("INVENTORY MANAGEMENT SYSTEM v1.0")
print("=" * 50)

if os.path.exists(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
else:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, price REAL)")
    cursor.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
    cursor.execute("INSERT INTO users VALUES ('admin', 'password123', 'admin')")
    cursor.execute("INSERT INTO users VALUES ('user1', 'pass123', 'user')")
    cursor.execute("INSERT INTO products VALUES (1, 'Laptop', 10, 999.99)")
    cursor.execute("INSERT INTO products VALUES (2, 'Mouse', 50, 19.99)")
    cursor.execute("INSERT INTO products VALUES (3, 'Keyboard', 30, 49.99)")
    cursor.execute("INSERT INTO products VALUES (4, 'Monitor', 15, 299.99)")
    cursor.execute("INSERT INTO products VALUES (5, 'USB Cable', 100, 5.99)")
    cursor.execute("INSERT INTO products VALUES (6, 'Headphones', 25, 79.99)")
    cursor.execute("INSERT INTO products VALUES (7, 'Webcam', 8, 89.99)")
    cursor.execute("INSERT INTO products VALUES (8, 'Microphone', 12, 129.99)")
    cursor.execute("INSERT INTO products VALUES (9, 'Desk Lamp', 20, 34.99)")
    cursor.execute("INSERT INTO products VALUES (10, 'Chair', 5, 199.99)")
    conn.commit()
    print("Database initialized with sample data!")

print("\n--- LOGIN ---")
username = input("Username: ")
password = input("Password: ")

query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
user = cursor.fetchone()

if user:
    current_user = username
    print("Login successful! Welcome %s" % username)
else:
    print("Invalid credentials!")
    conn.close()
    exit()

while True:
    print("\n" + "=" * 50)
    print("MAIN MENU")
    print("=" * 50)
    print("1. View All Products")
    print("2. Add New Product")
    print("3. Update Product Quantity")
    print("4. Search Product")
    print("5. Low Stock Report")
    print("6. Delete Product")
    print("7. Execute Custom Query (Admin Only)")
    print("8. Backup Data")
    print("9. Exit")
    print("=" * 50)
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        print("\n--- ALL PRODUCTS ---")
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        if len(products) == 0:
            print("No products found!")
        else:
            print("ID | Name | Quantity | Price")
            print("-" * 50)
            for p in products:
                print("%d | %s | %d | $%.2f" % (p[0], p[1], p[2], p[3]))
    
    elif choice == "2":
        print("\n--- ADD NEW PRODUCT ---")
        prod_id = input("Enter Product ID: ")
        prod_name = input("Enter Product Name: ")
        prod_qty = input("Enter Quantity: ")
        prod_price = input("Enter Price: ")
        
        query = "INSERT INTO products VALUES (" + prod_id + ", '" + prod_name + "', " + prod_qty + ", " + prod_price + ")"
        cursor.execute(query)
        conn.commit()
        print("Product added successfully!")
    
    elif choice == "3":
        print("\n--- UPDATE QUANTITY ---")
        prod_id = input("Enter Product ID: ")
        new_qty = input("Enter New Quantity: ")
        
        query = "UPDATE products SET quantity = " + new_qty + " WHERE id = " + prod_id
        cursor.execute(query)
        conn.commit()
        print("Quantity updated!")
    
    elif choice == "4":
        print("\n--- SEARCH PRODUCT ---")
        search_term = input("Enter product name or ID: ")
        
        query = "SELECT * FROM products WHERE name LIKE '%" + search_term + "%' OR id = " + search_term
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                print("No products found!")
            else:
                print("ID | Name | Quantity | Price")
                print("-" * 50)
                for p in results:
                    print("%d | %s | %d | $%.2f" % (p[0], p[1], p[2], p[3]))
        except:
            print("Search failed!")
    
    elif choice == "5":
        print("\n--- LOW STOCK REPORT ---")
        cursor.execute("SELECT * FROM products WHERE quantity < " + str(LOW_STOCK))
        low_stock = cursor.fetchall()
        if len(low_stock) == 0:
            print("All products are well stocked!")
        else:
            print("WARNING: The following products are low in stock:")
            print("ID | Name | Quantity | Price")
            print("-" * 50)
            for p in low_stock:
                print("%d | %s | %d | $%.2f" % (p[0], p[1], p[2], p[3]))
    
    elif choice == "6":
        print("\n--- DELETE PRODUCT ---")
        prod_id = input("Enter Product ID to delete: ")
        
        query = "DELETE FROM products WHERE id = " + prod_id
        cursor.execute(query)
        conn.commit()
        print("Product deleted!")
    
    elif choice == "7":
        if current_user == "admin":
            print("\n--- CUSTOM QUERY EXECUTION ---")
            print("WARNING: This feature is for advanced users only!")
            custom_query = input("Enter SQL query: ")
            
            cursor.execute(custom_query)
            try:
                results = cursor.fetchall()
                print("Query Results:")
                for row in results:
                    print(row)
                conn.commit()
            except:
                print("Query executed!")
                conn.commit()
        else:
            print("Access denied! Admin only feature.")
    
    elif choice == "8":
        print("\n--- BACKUP DATA ---")
        cursor.execute("SELECT * FROM products")
        all_products = cursor.fetchall()
        
        backup_file = open("backup.pkl", "wb")
        pickle.dump(all_products, backup_file)
        backup_file.close()
        print("Backup created successfully!")
    
    elif choice == "9":
        print("\nSaving changes...")
        conn.commit()
        conn.close()
        print("Goodbye!")
        break
    
    else:
        print("Invalid choice! Please try again.")

print("\nThank you for using Inventory Management System!")

# Made with Bob

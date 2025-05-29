from flask import Flask, request, jsonify
import base64
import hashlib
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ===================== База данных =====================
def get_db_connection():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ===================== API =====================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(force=True, silent=True)
    if not data:
        print("Неверный JSON")
        return jsonify({"error": "Invalid or missing JSON in request"}), 400

    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "Missing login or password"}), 400

    # Вычисляем хеш пароля
    hash_value = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE Login = ? AND Password = ?", 
                        (login, hash_value)).fetchone()
    conn.close()

    if user:
        token = base64.b64encode(f"{login}:{hash_value}".encode()).decode()
        return jsonify({"token": token, "role": "admin"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.get_json()
    required_fields = ["Rf_Products_Id", "CountProduct", "ContactUser"]

    # Проверка обязательных полей
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "Все поля обязательны"}), 400

    product_id = data["Rf_Products_Id"]
    count = data["CountProduct"]
    contact = data["ContactUser"]

    # Получаем сегодняшнюю дату
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем максимальный OrderCode за сегодня
    cursor.execute("""
        SELECT MAX(OrderCode) FROM orders 
        WHERE DATE(OrderDate) = ?
    """, (today,))
    max_code = cursor.fetchone()[0]
    next_code = (max_code or 0) + 1

    # Вставляем новый заказ
    cursor.execute("""
        INSERT INTO orders (Rf_Products_Id, CountProduct, ContactUser, OrderDate, OrderCode)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
    """, (product_id, count, contact, next_code))

    conn.commit()
    conn.close()

    return jsonify({"message": "Заказ оформлен", "order_code": next_code}), 201
   
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM Categories").fetchall()
    conn.close()
    return jsonify({"categories": [dict(row) for row in categories]})

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or "name" not in data or "code" not in data:
        return jsonify({"error": "Missing category name or code"}), 400

    category_name = data["name"]
    category_code = data["code"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (Names, Code) VALUES (?, ?)", (category_name, category_code))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": category_id, "name": category_name, "code": category_code}), 201

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    Удаляет категорию по ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем, существует ли категория
    category = cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    if category is None:
        conn.close()
        return jsonify({"error": "Category not found"}), 404

    # Удаляем категорию
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Category deleted"}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    category_id = request.args.get("category_id", type=int)
    if category_id is None:
        return jsonify({"error": "Missing category_id parameter"}), 400

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products WHERE Rf_CategoryId = ?", (category_id,)).fetchall()
    conn.close()
    return jsonify({"products": [dict(row) for row in products]})

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    required_fields = ["name", "count", "units", "description", "price", "Rf_Category_id"]
    
    # Проверка наличия всех нужных полей
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Отсутствуют обязательные поля"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, count, units, description, price, Rf_CategoryId)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["count"],
        data["units"],
        data["description"],
        data["price"],
        data["Rf_Category_id"]
    ))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": product_id,
        "name": data["name"],
        "Rf_Category_id": data["Rf_Category_id"]
    }), 201

@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    print(f"Получен запрос на обновление товара {product_id}: {data}")
    required_fields = ["name", "count", "units", "description", "price", "Rf_Category_id"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Не все поля переданы"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Products
        SET Name = ?, Count = ?, Units = ?, Description = ?, Price = ?, Rf_CategoryId = ?
        WHERE Products_Id = ?
    """, (
        data["name"],
        data["count"],
        data["units"],
        data["description"],
        data["price"],
        data["Rf_Category_id"],
        product_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Товар обновлён"}), 200

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Удаляет товар по ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, существует ли товар
    product = cursor.execute("SELECT * FROM products WHERE Products_Id = ?", (product_id,)).fetchone()
    if product is None:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    # Удаляем товар
    cursor.execute("DELETE FROM products WHERE Products_Id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import base64
import sqlite3

app = Flask(__name__)

# ===================== База данных =====================
def get_db_connection():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ===================== API =====================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    login = data.get("login")
    password = data.get("password")

    print(f"Login: {login}, Password: {password}")  # Отладка

    if not login or not password:
        return jsonify({"error": "Missing login or password"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE Login = ? AND password = ?", 
                        (login, password)).fetchone()
    conn.close()

    if user:
        print(f"User found: {user}")  # Отладка
        token = base64.b64encode(f"{login}:{password}".encode()).decode()
        return jsonify({"token": token, "role": "admin"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return jsonify({"categories": [dict(row) for row in categories]})

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing category name"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (data["name"],))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": category_id, "name": data["name"]}), 201

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
    products = conn.execute("SELECT * FROM products WHERE category_id = ?", (category_id,)).fetchall()
    conn.close()
    return jsonify({"products": [dict(row) for row in products]})

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or "name" not in data or "category_id" not in data:
        return jsonify({"error": "Missing product name or category_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category_id) VALUES (?, ?)", (data["name"], data["category_id"]))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": product_id, "name": data["name"], "category_id": data["category_id"]}), 201

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Удаляет товар по ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, существует ли товар
    product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    # Удаляем товар
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted"}), 200

# ===================== Шаблоны =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_panel')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/ovoshi')
def ovoshi():
    return render_template('ovoshi.html')

@app.route('/myaso')
def myaso():
    return render_template('myaso.html')

@app.route('/frukti')
def frukti():
    return render_template('frukti.html')

@app.route('/milk_prod')
def milk_prod():
    return render_template('milk_prod.html')

# ===================== Запуск =====================
if __name__ == '__main__':
    app.run(debug=True)

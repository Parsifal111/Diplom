from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    """
    Создает и возвращает соединение с базой данных SQLite.
    """
    try:
        conn = sqlite3.connect('my_database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        return {"error": f"Database connection error: {str(e)}"}, 500

@app.route('/api/login', methods=['POST'])
def login():
    """
    Авторизация пользователя.
    Проверяет логин и пароль в базе данных и возвращает токен при успешной авторизации.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON format"}), 400

    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "Missing login or password"}), 400

    conn = get_db_connection()
    if isinstance(conn, dict):  # Ошибка подключения к БД
        return jsonify(conn), 500

    try:
        user = conn.execute("SELECT id FROM users WHERE login = ? AND password = ?", (login, password)).fetchone()
        conn.close()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database query error: {str(e)}"}), 500

    if user:
        token = f"token-{user['id']}"
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    Получает список всех категорий из базы данных.
    """
    conn = get_db_connection()
    if isinstance(conn, dict):
        return jsonify(conn), 500

    try:
        categories = conn.execute("SELECT * FROM categories").fetchall()
        conn.close()
        return jsonify({"categories": [dict(row) for row in categories]})
    except sqlite3.Error as e:
        return jsonify({"error": f"Database query error: {str(e)}"}), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    """
    Создает новую категорию.
    """
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing category name"}), 400

    conn = get_db_connection()
    if isinstance(conn, dict):
        return jsonify(conn), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (data["name"],))
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": category_id, "name": data["name"]}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database insert error: {str(e)}"}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Получает список товаров по идентификатору категории.
    """
    category_id = request.args.get("category_id", type=int)
    if category_id is None:
        return jsonify({"error": "Missing category_id parameter"}), 400

    conn = get_db_connection()
    if isinstance(conn, dict):
        return jsonify(conn), 500

    try:
        products = conn.execute("SELECT * FROM products WHERE category_id = ?", (category_id,)).fetchall()
        conn.close()
        return jsonify({"products": [dict(row) for row in products]})
    except sqlite3.Error as e:
        return jsonify({"error": f"Database query error: {str(e)}"}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Создает новый товар.
    """
    data = request.get_json()
    if not data or "name" not in data or "category_id" not in data:
        return jsonify({"error": "Missing product name or category_id"}), 400

    conn = get_db_connection()
    if isinstance(conn, dict):
        return jsonify(conn), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, category_id) VALUES (?, ?)", (data["name"], data["category_id"]))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": product_id, "name": data["name"], "category_id": data["category_id"]}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database insert error: {str(e)}"}), 500

if __name__ == '__main__':
    """
    Запускает Flask-приложение в режиме отладки.
    """
    app.run(debug=True)



import sqlite3

def add_admin_user():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    login = "Admin"
    password = "123456"
    role = "admin"

    cursor.execute("INSERT INTO users (Login, password, Description) VALUES (?, ?, ?)",
                   (login, password, role))
    conn.commit()
    print("Пользователь добавлен!")

    conn.close()

if __name__ == "__main__":
    add_admin_user()

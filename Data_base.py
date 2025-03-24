import sqlite3

# Подключение к базе данных (или создание новой базы данных)
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Включаем поддержку внешних ключей
cursor.execute("PRAGMA foreign_keys = ON;")

# Создание таблицы users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    Login VARCHAR(50) NOT NULL,
    Password VARCHAR(50) NOT NULL,
    Description VARCHAR(200)
);
''')

# Создание таблицы Categories
cursor.execute('''
CREATE TABLE IF NOT EXISTS Categories (
    CategoryId INTEGER PRIMARY KEY AUTOINCREMENT,
    Names VARCHAR(150) NOT NULL,
    Code INTEGER NOT NULL,
    Photo VARCHAR(50)
);
''')

# Создание таблицы Products
cursor.execute('''
CREATE TABLE IF NOT EXISTS Products (
    Products_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Rf_CategoryId INTEGER,
    Name VARCHAR(150) NOT NULL,
    Count INTEGER NOT NULL,
    Units VARCHAR(10) NOT NULL,
    Description VARCHAR(500),
    Price INTEGER NOT NULL,
    FOREIGN KEY (Rf_CategoryId) REFERENCES Categories(CategoryId)
);
''')

# Создание таблицы Orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    OrderId INTEGER PRIMARY KEY AUTOINCREMENT,
    Rf_ProguctId INTEGER,
    CountProduct INTEGER NOT NULL,
    OrderCode INTEGER NOT NULL,
    ContactUser VARCHAR(100) NOT NULL,
    FOREIGN KEY (Rf_ProguctId) REFERENCES Products(Products_Id)
);
''')

# Сохранение изменений и закрытие соединения
conn.commit()

# Закрытие соединения с базой данных
conn.close()

print("База данных и таблицы успешно созданы.")


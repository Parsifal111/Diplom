# Этап 1: Python + Flask
FROM python:3.11-slim

# Установка Nginx
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем backend и базу данных
COPY back/app.py ./back/app.py
COPY my_database.db ./

# Копируем фронтенд
COPY front/ ./front/

# Копируем конфиг для nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Открываем порт
EXPOSE 80

# Запуск: сначала nginx, потом flask
CMD service nginx start && python back/app.py

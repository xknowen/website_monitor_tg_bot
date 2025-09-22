FROM python:3.11-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "-m", "app.services.main"]

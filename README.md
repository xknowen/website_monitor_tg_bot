# Website Monitor Telegram Bot

##  Описание проекта
Этот проект предназначен для мониторинга доступности веб-сайтов.  
Он периодически проверяет сайты и сохраняет результаты (статус ответа, время отклика, доступность) в базе данных.  
Управление осуществляется через Telegram-бота.

---

##  Инструкция по запуску

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/xknowen/website_monitor_tg_bot.git
cd website_monitor_tg_bot
```

### 2. Создайте виртуальное окружение и активируйте его
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Создайте файл `.env` в корне проекта
Пример:
```env
BOT_TOKEN=ваш_токен_бота
DATABASE_URL=sqlite+aiosqlite:///./site_monitor.db
CHECK_TIMEOUT=10
DEFAULT_INTERVAL=60
```

### 5. Запустите приложение
```bash
python -m app.main
```

### 6. Запустите тесты
```bash
pytest -q
```

> 💡 База SQLite создаётся автоматически при первом запуске (`site_monitor.db` в корне проекта).

---

##  Архитектура проекта
```
app/
├── api/              # Маршруты API (sites, checks)
├── core/             # Конфигурации и логгер
├── db/               # Модели, CRUD, подключение к БД
├── services/         # Логика мониторинга
├── main.py           # Точка входа
tests/                # Тесты
.env.example          # Пример переменных окружения
requirements.txt      # Зависимости
```

---

## 🗄 Схема базы данных
```
Site
- id (PK)
- url (string)
- created_at (datetime)

Check
- id (PK)
- site_id (FK -> Site.id)
- status (int, nullable)
- response_time (float, nullable)
- is_available (bool)
- checked_at (datetime)
```

---

## ⚙️ Настройка базы данных
По умолчанию используется SQLite.  
Если требуется PostgreSQL или другая СУБД:
1. Установите драйвер (например, asyncpg).
2. Укажите строку подключения в `.env`, например:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/monitor
```

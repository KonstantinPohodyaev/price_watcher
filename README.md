# 📉 Price Watcher Bot

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-0?logo=fastapi&logoColor=white&labelColor=009688&color=009688)
![fastapi-users](https://img.shields.io/badge/fastapi--users-14.0.1-blueviolet?logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.40-orange?logo=sqlalchemy)
![Alembic](https://img.shields.io/badge/Alembic-1.15.2-3796b0?logo=alembic)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![Telegram Bot](https://img.shields.io/badge/python--telegram--bot-22.1-34A5DB?logo=telegram)
![AIOHTTP](https://img.shields.io/badge/aiohttp-3.11.18-005571?logo=python)
![uvicorn](https://img.shields.io/badge/uvicorn-0.34.1-black?logo=fastapi)

> 🛍️ Telegram-бот для отслеживания цен на маркетплейсах. Пользователи могут подписываться на
товары, и при снижении цены бот пришлёт уведомление! Так же есть возможность отслеживания истории товаров,
удобная авторизация.

---

## 🚀 Возможности

### 🧠 Backend (FastAPI + SQLAlchemy + PostgreSQL)

- 📡 Асинхронный FastAPI-сервер с чистой модульной архитектурой
- 🔐 **Кастомная авторизация и аутентификация**:
  - JWT-токены с шифрованием (Fernet) и хранением в БД
  - Пользовательская логика авторизации через `fastapi-users`
- 📊 CRUD-операции через SQLAlchemy 2.0 + Pydantic
- 🧩 Бизнес-логика:
  - Ограничение количества отслеживаний на товар
  - Хранение аватаров пользователей
  - Поддержка кастомных фильтров и пользовательских предпочтений
  - Надёжная валидация: десятки кастомных валидаторов на бизнес-логику

### 🤖 Telegram-бот

- 🎨 Удобный и **интуитивный интерфейс без накопления сообщений**
- 🔐 Авторизация и регистрация прямо в Telegram через `JWT`
- 🔔 Уведомления о снижении цен (интеграция с API Wildberries/Ozon)
- 🕓 Регулярная проверка цен и фоновое обновление данных о товаре через `APScheduler`

### ⚙️ DevOps и инфраструктура

- 📦 **Docker + Docker Compose**: развёртывание всех компонентов
- 🧾 Alembic для миграций БД (автоапгрейд при запуске)
- 🌐 Nginx как реверс-прокси
- 📂 Работа со статическими файлами (аватары)
- 🔐 Конфигурация через `.env`, гибкая настройка окружений

---

---

## ⚙️ Установка

```bash
git clone https://github.com/KonstantinPohodyaev/price_watcher.git
cd price_watcher
```

Создайте виртуальное окружение и активируйте его:

```bash
python -m venv venv
source venv/bin/activate  # Windows: . venv\Scripts\activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

### 📦 Переменные окружения

Создайте `.env` файл в корне проекта:

```env
# === DATABASE CONFIGURATION ===
DB_DIALECT=postgresql               # Диалект базы данных (используется SQLAlchemy/Alembic)
DB_DRIVER=asyncpg                   # Драйвер подключения к PostgreSQL (асинхронный)
DB_USERNAME=db_username             # Имя пользователя для подключения к базе
DB_PASSWORD=db_password             # Пароль для подключения к базе
DB_NAME=test_db.db                  # Название базы данных
DB_HOST=db                          # Хост базы данных (имя контейнера db)
DB_PORT=5432                        # Порт PostgreSQL в контейнере

# === POSTGRES CONTAINER CONFIGURATION ===
POSTGRES_USER=user                 # Пользователь PostgreSQL (используется в контейнере)
POSTGRES_PASSWORD=password         # Пароль PostgreSQL (используется в контейнере)
POSTGRES_DB=db                     # Имя БД PostgreSQL (используется в контейнере)
POSTGRES_PORT=5432                 # Порт PostgreSQL (должен совпадать с DB_PORT)
POSTGRES_HOST=db                   # Хост PostgreSQL (имя контейнера db)

# === APPLICATION CONFIG ===
SECRET=SECRET                      # Секретное значение (например, для подписи токенов)
TITLE=Price Watcher                # Название API
DESCRIPTION=Сервис для мониторинга цен.  # Описание API

# === SUPERUSER CONFIG ===
FIRST_SUPERUSER_EMAIL=your_email@.main.ru   # Email первого суперпользователя
FIRST_SUPERUSER_PASSWORD=your_password # Пароль первого суперпользователя

# === JWT CONFIGURATION ===
JWT_SECRET_KEY=A8zOVVp4FMb93RD03n0O25FwAYmTxmTQhF3kPBnLJ6E=  # Ключ для подписи JWT токенов. Base64-кодированная строка длиной 32 байта (в виде 44 символов, включая =)

# === TELEGRAM BOT ===
TELEGRAM_BOT_TOKEN=your_telegram_token  # Токен Telegram-бота (получить через BotFather в Telegram)

# === INTERNAL DOCKER NETWORK CONFIG ===
API_CONTAINER=api                 # Имя контейнера с API
API_PORT=8000                     # Порт API внутри Docker
PROTOCOL=http                     # Протокол (http или https)
```
---

## ▶️ Запуск в отдельных терминалах для тестирования

### Выполнение Миграций
```bash
alembic upgrade head
```

### Запуск backend-сервера:

```bash
uvicorn src.main:app
```

### Запуск Telegram-бота:

```bash
python -m bot.main
```

_API будет доступно по ```http://127.0.0.1:8000/docs```_

## ▶️ Запуск в Docker-контейнерах (для Windows)
_Перед выполнением команды необходимо запустить Docker Desktop_

### Запуск контейнеров:

```bash
docker compose up -d
```

### Остановка контейнеров
```bash
docker compose down
```

_API будет доступно по ```http://localhost/docs```_

---

## 📌 Пример использования

1. Пользователь регистрируется или авторизуется через FastAPI в боте.
2. В Telegram выбирает маркетплейс, отправляет артикул на товар, желаемую цену.
3. Бот сохраняет артикул и через API выбранного маркетплейса получает всю необходимую информацию.
4. На каждом этапе происходит валидация и проверка данных и действий со стороны пользователя.
5. Есть возможность включить уведомления и узнать когда цена на товар упадет до желаемой.
6. При снижении — приходит сообщение 📩 в Telegram.
7. Есть возможность редактирования настройки аккаунта, товаров, изменения желаемой цены, просмотра истории цен и тд.

---

## 👨‍💻 Автор

**Походяев Константин**  
Telegram: [@kspohodyaev](https://t.me/kspohodyaev)

---

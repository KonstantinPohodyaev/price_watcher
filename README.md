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

- 📡 Асинхронный FastAPI backend с поддержкой `JWT` авторизации
- 🧑‍💻 Авторизация через `fastapi-users`
- 🔔 Telegram-бот оповещает при снижении цены
- 🛍️ Поддержка разных маркетплейсов (через API)
- 🧠 Хранение отслеживаемых товаров в БД (до SQLite/PostgreSQL)
- 🕒 Периодическая проверка цен с помощью `APScheduler`
- 💌 Уведомления через `python-telegram-bot`

---

## ⚙️ Установка

```bash
git clone https://github.com/KonstantinPohodyaev/price_watcher.git
cd price_watcher
```

Создайте виртуальное окружение и активируйте его:

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

### 📦 Переменные окружения

Создайте `.env` файл в корне проекта:

```env
```env
DATABASE_URL=sqlite+aiosqlite:///test.db      # Полный URL подключения к БД
DB_DIALECT=sqlite                              # Диалект базы данных (например, sqlite, postgresql)
DB_DRIVER=aiosqlite                            # Драйвер БД
DB_USERNAME=db_username                        # Имя пользователя БД (для PostgreSQL и др.)
DB_PASSWORD=db_password                        # Пароль пользователя БД
DB_NAME=test_db.db                             # Название БД или путь к .db-файлу
DB_HOST=db                                    # Хост БД (например, localhost или db в Docker)
DB_PORT=5432                                  # Порт подключения к БД (по умолчанию 5432 для PostgreSQL)

SECRET=SECRET                                 # Секретный ключ приложения

TITLE=Price Watcher                           # Название приложения (отображается в OpenAPI)
DESCRIPTION=Сервис для мониторинга цен.      # Описание API (OpenAPI)

FIRST_SUPERUSER_EMAIL=k@mail.ru               # Email суперпользователя
FIRST_SUPERUSER_PASSWORD=1234                  # Пароль суперпользователя

TELEGRAM_BOT_TOKEN=your_token                 # Токен Telegram-бота от @BotFather
JWT_SECRET_KEY=A8zOVVp4FMb93RD03n0O25FwAYmTxmTQhF3kPBnLJ6E=  # Секрет для JWT-токенов
```

---

## 🧱 Миграции БД

```bash
alembic upgrade head
```

---

## ▶️ Запуск (в отдельных терминалах для тестирования)

### Запуск backend-сервера:

```bash
uvicorn src.main:app
```

### Запуск Telegram-бота:

```bash
python -m bot.main
```

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

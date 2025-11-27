# Инструкция по запуску (Этап 1 - Базовая структура)

## Предварительные требования

- Python 3.11+
- Git
- SQLite (уже установлен в системе)

## Быстрый старт

### 1. Установка зависимостей

```bash
# Установить все зависимости
make install

# Или по отдельности:
make install-backend  # Только backend
make install-bot      # Только bot
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

Обязательные переменные:
- `TELEGRAM_TOKEN` - токен от @BotFather
- `YANDEX_API_KEY` - ключ API Яндекс.Карт

### 3. Запуск

```bash
# Запустить backend и bot одновременно
make dev

# Или по отдельности:
make dev-backend  # Backend на http://localhost:8000
make dev-bot      # Telegram bot
```

## Структура проекта

```
backend/
├── app/
│   ├── api/          # API endpoints (будет в Этапе 2)
│   ├── core/         # Конфигурация, логирование, кэш
│   ├── db/           # Модели БД и сессии
│   ├── schemas/      # Pydantic схемы
│   ├── services/     # Бизнес-логика (будет в Этапе 2)
│   ├── repositories/ # Работа с БД (будет в Этапе 2)
│   └── main.py       # Точка входа FastAPI
├── tests/            # Тесты
├── requirements.txt
└── .venv/

bot/
├── app/
│   ├── handlers/     # Обработчики (будет в Этапе 3)
│   ├── keyboards/    # Клавиатуры (будет в Этапе 3)
│   ├── services/     # API клиент
│   ├── states/       # FSM состояния (будет в Этапе 3)
│   ├── config.py     # Конфигурация
│   └── main.py       # Точка входа бота
├── tests/
├── requirements.txt
└── .venv/
```

## Что реализовано в Этапе 1

✅ **Backend:**
- Базовая структура FastAPI приложения
- Конфигурация с поддержкой SQLite и PostgreSQL
- SQLAlchemy модели для всех таблиц
- Система логирования
- In-memory кэш
- Health check эндпоинты

✅ **Bot:**
- Базовая структура aiogram бота
- Конфигурация
- HTTP клиент для API
- MemoryStorage для FSM

✅ **Инфраструктура:**
- Makefile для автоматизации
- requirements.txt для обоих проектов
- .env.example с примерами настроек

## Проверка работы

### Backend

```bash
# Запустить backend
make dev-backend

# В другом терминале проверить:
curl http://localhost:8000/
curl http://localhost:8000/health
```

Откройте http://localhost:8000/docs для Swagger UI

### Bot

```bash
# Запустить бота
make dev-bot

# Бот должен запуститься без ошибок
# Пока обработчиков нет, но структура готова
```

## Следующие шаги

**Этап 2:** Реализация Backend API
- Repositories для работы с БД
- Services с бизнес-логикой
- API endpoints для всех сущностей
- Интеграция с Yandex Maps

**Этап 3:** Реализация Telegram Bot
- Обработчики команд
- FSM для поиска врачей
- Клавиатуры с пагинацией
- Интеграция с Backend API

## Полезные команды

```bash
# Форматирование кода
make format

# Проверка линтером
make lint

# Запуск тестов (когда будут написаны)
make test

# Очистка виртуальных окружений
make clean
```

## Troubleshooting

**Ошибка: "TELEGRAM_TOKEN is required"**
- Проверьте, что создан файл `.env`
- Убедитесь, что в нем указан `TELEGRAM_TOKEN`

**Ошибка: "YANDEX_API_KEY is required"**
- Добавьте `YANDEX_API_KEY` в `.env`

**Backend не запускается**
- Проверьте, что установлены зависимости: `make install-backend`
- Проверьте, что порт 8000 свободен

**База данных не найдена**
- Убедитесь, что файл `medical_data.db` находится в корне проекта
- Проверьте `DATABASE_PATH` в `.env`

---

**Статус:** Этап 1 завершен ✅  
**Дата:** 2025-01-13

## Запуск проекта (о программе смотри внизу)



### 1. Клонировать репозиторий

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Создать файл `.env`

Создайте файл `.env` (если его нет) / отредактируйте

Пример:

```env
APP_NAME=File Analyzer
APP_ENV=development
APP_DEBUG=true

POSTGRES_DB=file_analyzer
POSTGRES_USER=file_analyzer
POSTGRES_PASSWORD=file_analyzer
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

SOURCE_API_URL=http://example.com
SOURCE_API_CANDIDATE_ID=your_id
SOURCE_API_TIMEOUT_SECONDS=30

STORAGE_ROOT=/app/storage

NOVOSIBIRSK_TIMEZONE=Asia/Novosibirsk
```

### 3. Собрать и запустить приложение

```bash
docker compose up --build
```

После запуска автоматически будут:

- подняты PostgreSQL и Redis;
- применены миграции Alembic;
- запущен FastAPI;
- запущен Celery Worker.

## Проверка работы

После запуска приложение будет доступно по адресу:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

Проверка состояния приложения:

```
http://127.0.0.1:8000/health
```

Ответ:

```json
{
  "status": "ok"
}
```


# О программе
## Используемые сервисы

| Сервис | Назначение |
|---------|------------|
| PostgreSQL | хранение данных |
| Redis | брокер сообщений Celery |
| Celery Worker | фоновая обработка задач |
| FastAPI | HTTP API приложения |

## Хранение файлов

Все загруженные файлы сохраняются в Docker Volume и доступны как FastAPI, так и Celery Worker.

## Остановка приложения

```bash
docker compose down
```

Для удаления контейнеров вместе с томами данных:

```bash
docker compose down -v
```

## Возможности

- создание асинхронной задачи на загрузку файлов;
- получение информации о состоянии задачи;
- загрузка файлов из внешнего API;
- обработка задач в фоновом режиме;
- сохранение информации о задачах и файлах в PostgreSQL;
- хранение загруженных файлов в Docker Volume;
- проверка ZIP-архивов;
- защита от Zip Slip;
- автоматическое применение миграций Alembic;
- интерактивная документация Swagger;
- запуск всего приложения через Docker Compose.

## Технологический стек

- Python 3.13.7;
- FastAPI;
- SQLAlchemy 2;
- PostgreSQL;
- Alembic;
- Celery;
- Redis;
- HTTPX;
- Pydantic Settings;
- Jinja2;
- Docker;
- Docker Compose.

## Архитектура

Проект разделён на несколько слоёв:

```text
app/
├── api/             # HTTP API, роутеры и зависимости
├── clients/         # клиенты для взаимодействия с внешними API
├── core/            # конфигурация приложения
├── db/              # настройка базы данных и ORM-модели
├── repositories/    # работа с базой данных
├── services/        # бизнес-логика приложения
├── tasks/           # фоновые задачи Celery
├── templates/       # HTML-шаблоны
├── static/          # статические файлы
└── main.py          # точка входа FastAPI

migrations/          # миграции Alembic
storage/downloaded/  # локальное хранилище загруженных файлов
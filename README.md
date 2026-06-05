# АСУБ — Автоматизированная система управления библиотекой

Веб-приложение для управления книжным фондом, читателями и выдачей литературы. Поддерживает роли: Читатель, Библиотекарь, Администратор.

## Быстрый старт

### Локальный запуск

```bash
# 1. Установка зависимостей
make install-dev

# 2. Запуск приложения
make run

# 3. Открыть в браузере
# http://localhost:5000
```

### Запуск в Docker

```bash
# Сборка и запуск
make docker-up

# Проверка
curl http://localhost:5000

# Остановка (данные сохраняются)
make docker-stop

# Полная очистка с удалением данных
make docker-down
```

## Требования

- Python ≥ 3.12
- Docker + Docker Compose (для контейнерного запуска)
- Git

## Основные команды

| Команда | Описание |
|---------|----------|
| `make install-dev` | Установка с dev-зависимостями |
| `make install-prod` | Установка из TestPyPI |
| `make install` | Установка из lock-файла |
| `make run` | Запуск Flask локально |
| `make test` | Запуск тестов |
| `make coverage` | Отчёт о покрытии тестами |
| `make docker-build` | Сборка Docker-образа |
| `make docker-up` | Запуск в Docker Compose |
| `make docker-stop` | Остановка Compose (сохранить данные) |
| `make docker-down` | Остановка Compose (удалить данные) |
| `make docker-logs` | Просмотр логов контейнера |
| `make docker-shell` | Shell внутри контейнера |
| `make docs` | Сборка документации (MkDocs) |
| `make reset-db` | Удаление файла базы данных |
| `make clean` | Очистка кэша и артефактов |
| `make help` | Справка по командам |

## Структура репозитория

```
library-db-app/
├── src/app/              # Flask-приложение
│   ├── routes/           # Роуты (auth, public, reader, librarian, admin)
│   ├── static/           # CSS, JS
│   ├── templates/        # HTML-шаблоны (Jinja2)
│   ├── csv/              # Начальные данные
│   ├── main.py           # Точка входа
│   ├── repository.py     # Бизнес-логика
│   └── export_reports.py # Экспорт CSV/PDF
├── tests/                # Тесты (pytest)
│   ├── conftest.py       # Фикстуры
│   ├── test_auth.py
│   ├── test_public.py
│   ├── test_reader.py
│   ├── test_librarian.py
│   └── test_admin.py
├── docs/                 # Документация (MkDocs)
│   ├── index.md
│   ├── specification.md
│   ├── architecture.md
│   ├── use_cases.md
│   ├── sql_queries.md
│   ├── diagrams.md
│   └── diagrams/         # .drawio.png исходники
├── infra/                # Docker Compose
│   └── compose.yaml
├── Dockerfile            # Образ приложения
├── .dockerignore
├── Makefile              # Автоматизация
├── requirements.txt      # Зависимости (TestPyPI)
├── requirements.lock     # Фиксированные версии
├── pyproject.toml        # Метаданные проекта
└── mkdocs.yml            # Конфигурация документации
```

## Репозитории

| Репозиторий | Назначение |
|-------------|-----------|
| [library-db-app](https://github.com/HotGodDog/library-db-app) | Это приложение (Flask) |
| [library-db-core](https://github.com/HotGodDog/library-db-core) | Ядро — доступ к SQLite (TestPyPI) |

## Документация

Собирается автоматически:

```bash
make docs
# Результат в site/
```

Или локальный сервер:

```bash
mkdocs serve
# http://127.0.0.1:8000
```

## Тесты

```bash
make test        # запуск
make coverage    # с отчётом о покрытии
```

Покрытие: **76%** (43/43 тестов проходят).

## Технологии

- **Backend:** Flask 3.x, Python 3.12+
- **База данных:** SQLite (триггеры, миграции)
- **Ядро:** [library-db-core](https://test.pypi.org/project/library-db-core/) (TestPyPI)
- **Контейнеризация:** Docker, Docker Compose
- **Тесты:** pytest, pytest-cov
- **Документация:** MkDocs
- **Отчёты:** fpdf2 (PDF), CSV

## Лицензия

MIT

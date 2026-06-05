# АСУБ — Автоматизированная система управления библиотекой

Веб-приложение для управления библиотечным фондом, читателями и выдачей книг.

## Быстрый старт

```bash
# Установка
make install-dev

# Запуск локально
make run

# Тесты
make test

# Покрытие
make coverage

# Docker
make docker-up
```

## Структура репозитория

| Папка | Назначение |
|-------|-----------|
| `src/app/` | Flask-приложение (роуты, шаблоны, статика) |
| `tests/` | Проверочные тесты (pytest) |
| `docs/` | Документация (MkDocs) |
| `infra/` | Docker Compose |

## Репозитории

- [library-db-app](https://github.com/HotGodDog/library-db-app) — это приложение
- [library-db-core](https://github.com/HotGodDog/library-db-core) — ядро (TestPyPI)

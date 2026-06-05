# Архитектура

## Разделение ответственности

Проект состоит из двух частей:

| Часть | Тип | Назначение |
|-------|-----|-----------|
| `library-db-core` | Переиспользуемый пакет (TestPyPI) | Доступ к SQLite, модели данных, SQL-схема |
| `library-db-app` | Запускаемое приложение | Веб-интерфейс (Flask), бизнес-логика, отчёты |

## Слои приложения

| Компонент | Технология |
|-----------|------------|
| Presentation | HTML, CSS, JS |
| Application | Flask routes |
| Domain | Repository pattern |
| Data | library-db-core |
| Storage | SQLite (file) |


## Технологии

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Backend | Flask | ≥3.0 |
| База данных | SQLite | 3.x |
| Ядро | library-db-core | ≥0.3.0 |
| PDF-отчёты | fpdf2 | ≥2.7 |
| Тесты | pytest | ≥8.0 |
| Документация | MkDocs | latest |

## Контейнеризация

Приложение запускается в Docker с именованным volume для БД:

```bash
make docker-up
```

Переменная `LIBRARY_DB_PATH=/data/library.db` задаёт путь к базе внутри контейнера.

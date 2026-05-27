.PHONY: install run test lint clean help

# Установка
install:
	pip install -r requirements.txt

# Запуск
run:
	flask --app src/app run --debug

# Очистка кэша
clean-cache:
	@echo "clean-cache..."
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Тесты
test: clean-cache
	PYTHONPATH=. pytest tests/ -v --tb=short

# Сброс БД
reset-db:
	rm -f library.db

# Полная перезагрузка
reset: clean reset-db
	@echo "Проект сброшен. Запустите 'make run' для создания новой БД."

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make install        - Установка зависимостей"
	@echo "  make run            - Запуск приложения"
	@echo "  make test           - Запуск тестов"
	@echo "  make reset-db       - Удаление файла базы данных"
	@echo "  make reset          - Полный сброс проекта"

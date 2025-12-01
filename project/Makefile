.PHONY: help up-database down-database stop-database restart-database logs-database status-database shell-database clean-database

# Определение команды docker-compose (автоматически)
DOCKER_COMPOSE := docker compose

help: ## Показать справку по командам
	@echo "Доступные команды для работы с базой данных:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

up-database: ## Запустить PostgreSQL в Docker контейнере
	@if [ ! -f .env ]; then touch .env; fi; \
	if ! grep -q "^DOCKER_DB_PORT=" .env 2>/dev/null; then \
		echo "Порт для PostgreSQL контейнера не указан."; \
		read -p "На каком порту запустить PostgreSQL? [5433]: " port; \
		port=$${port:-5433}; \
		echo "DOCKER_DB_PORT=$$port" >> .env; \
		echo "Порт $$port сохранен в .env"; \
	fi; \
	if ! grep -q "^DB_NAME=" .env 2>/dev/null; then \
		read -p "Имя базы данных [askpupkin]: " db_name; \
		db_name=$${db_name:-askpupkin}; \
		echo "DB_NAME=$$db_name" >> .env; \
	fi; \
	if ! grep -q "^DB_USER=" .env 2>/dev/null; then \
		read -p "Пользователь БД [postgres]: " db_user; \
		db_user=$${db_user:-postgres}; \
		echo "DB_USER=$$db_user" >> .env; \
	fi; \
	if ! grep -q "^DB_PASSWORD=" .env 2>/dev/null; then \
		read -p "Пароль БД [postgres]: " db_password; \
		db_password=$${db_password:-postgres}; \
		echo "DB_PASSWORD=$$db_password" >> .env; \
	fi; \
	if ! grep -q "^DB_HOST=" .env 2>/dev/null; then \
		echo "DB_HOST=localhost" >> .env; \
	fi; \
	export $$(grep -v '^#' .env | xargs 2>/dev/null); \
	echo "Запуск PostgreSQL на порту $$DOCKER_DB_PORT..."; \
	DOCKER_DB_PORT=$$DOCKER_DB_PORT $(DOCKER_COMPOSE) up -d postgres; \
	echo "PostgreSQL запущен на порту $$DOCKER_DB_PORT"

down-database: ## Остановить и удалить контейнер (данные сохраняются)
	@echo "Остановка PostgreSQL..."
	@$(DOCKER_COMPOSE) down
	@echo "Контейнер остановлен"

stop-database: ## Остановить контейнер без удаления
	@echo "Остановка PostgreSQL..."
	@$(DOCKER_COMPOSE) stop postgres
	@echo "Контейнер остановлен"

restart-database: ## Перезапустить контейнер
	@echo "Перезапуск PostgreSQL..."
	@$(DOCKER_COMPOSE) restart postgres
	@echo "Контейнер перезапущен"

logs-database: ## Показать логи PostgreSQL
	@$(DOCKER_COMPOSE) logs -f postgres

status-database: ## Показать статус контейнера
	@echo "Статус PostgreSQL:"
	@$(DOCKER_COMPOSE) ps postgres

shell-database: ## Подключиться к PostgreSQL через psql
	@$(DOCKER_COMPOSE) exec postgres psql -U postgres -d askpupkin

clean-database: ## Удалить контейнер и все данные (ОПАСНО!)
	@echo "ВНИМАНИЕ: Это удалит все данные в базе!"
	@read -p "Вы уверены? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@$(DOCKER_COMPOSE) down -v
	@echo "Контейнер и данные удалены"


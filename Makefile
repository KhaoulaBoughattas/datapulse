COMPOSE = docker compose -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: up down ps logs psql smoke-test clean

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f

psql:
	docker exec -it datapulse-postgres psql -U datapulse -d datapulse

smoke-test:
	python scripts/smoke_test_db.py

clean:
	$(COMPOSE) down -v

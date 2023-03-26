# инструкция по работе с файлом "Makefile" – https://bytes.usc.edu/cs104/wiki/makefile/

# обновление сборки Docker-контейнера
build:
	docker compose build

# генерация документации
docs-html:
	docker compose run --no-deps --workdir /docs favorite-places-app /bin/bash -c "make html"

# запуск форматирования кода
format:
	docker compose run --no-deps --workdir / favorite-places-app /bin/bash -c "black src docs/source/*.py; isort --profile black src docs/source/*.py"

# запуск статического анализа кода (выявление ошибок типов и форматирования кода)
lint:
	docker compose run --no-deps --workdir / favorite-places-app /bin/bash -c "pylint src; flake8 src; mypy src; black --check src"

# создание базы данных
db:
	docker compose up -d favorite-places-db

# миграции	
migrate:
	docker compose run favorite-places-app alembic upgrade head	
	
# запуск автоматических тестов
test:
	docker compose run favorite-places-app pytest --cov=/src --cov-report html:htmlcov --cov-report term --cov-config=/src/tests/.coveragerc -vv

# запуск всех функций поддержки качества кода
all: format lint test

DEV_BIND_DIR := "."

DEV_IMAGE := exam-manage-dev

DOCKER_NON_INTERACTIVE ?= false

DEV_MOUNT := -v "$(CURDIR)/$(DEV_BIND_DIR):/var/task/$(DEV_BIND_DIR)"
DEV_ENVS := \
	-e DB_HOST \
	-e DB_PORT \
	-e DB_NAME \
	-e DB_USER \
	-e DB_USER_PASSWORD \
	-e DJANGO_SECRET_KEY
DOCKER_RUN_DEV_OPTS := $(DEV_ENVS) $(DEV_MOUNT) "$(DEV_IMAGE)"
DOCKER_RUN_DEV := docker run $(if $(DOCKER_NON_INTERACTIVE), , -it) $(DOCKER_RUN_DEV_OPTS)

PRE_DEV_TARGET ?= build-dev-image

default: app

## Build Dev Docker image
build-dev-image:
	DOCKER_BUILDKIT=1 docker build -t "$(DEV_IMAGE)" -f dev.Dockerfile .

## Run dev server
up:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up -d --build

# Logs for web container
logs:
	docker-compose logs -f web

down:
	docker-compose down

migrate:
	docker-compose exec web python exammanagement/manage.py migrate

make_migrations:
	docker-compose exec web python exammanagement/manage.py makemigrations

show_migrations:
	docker-compose exec web python exammanagement/manage.py showmigrations

seed_migrations:
	docker-compose exec web python exammanagement/manage.py makemigrations --empty main --name $(name)

createsuperuser:
	docker-compose exec web python exammanagement/manage.py createsuperuser

test: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) python exammanagement/manage.py test

lint: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) pre-commit run --all-files

## Generate requirements files
requirements: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) ./script/requirements.sh

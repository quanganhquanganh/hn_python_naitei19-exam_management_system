BUILD_BIND_DIR := "dist"
DEV_BIND_DIR := "."

BUILD_IMAGE := exam-manage-build
DEV_IMAGE := exam-manage-dev
DEPLOY_IMAGE := exam-manage-deploy

DOCKER_NON_INTERACTIVE ?= false

BUILD_MOUNT := -v "$(CURDIR)/$(BUILD_BIND_DIR):/var/task/$(BUILD_BIND_DIR)"
DOCKER_RUN_BUILD_OPTS := $(BUILD_MOUNT) "$(BUILD_IMAGE)"
DOCKER_RUN_BUILD := docker run $(if $(DOCKER_NON_INTERACTIVE), , -it) $(DOCKER_RUN_BUILD_OPTS)
DOCKER_RUN_BUILD_NOTTY := docker run $(if $(DOCKER_NON_INTERACTIVE), , -i) $(DOCKER_RUN_BUILD_OPTS)

DEV_MOUNT := -v "$(CURDIR)/$(DEV_BIND_DIR):/var/task/$(DEV_BIND_DIR)"
DEV_ENVS := \
	-e DB_HOST \
	-e DB_PORT \
	-e DB_NAME \
	-e DB_USER \
	-e DB_PASSWORD \
	-e DJANGO_SUPERUSER_EMAIL \
	-e DJANGO_SUPERUSER_PASSWORD \
	-e DJANGO_SUPERUSER_USERNAME \
	-e DJANGO_SECRET_KEY \
	-e STATIC_ROOT \
	-e ENABLE_COLLECTSTATIC_S3 \
	-e AWS_S3_ACCESS_KEY_ID_STATIC \
	-e AWS_S3_SECRET_ACCESS_KEY_STATIC \
	-e AWS_REGION_STATIC \
	-e AWS_S3_BUCKET_NAME_STATIC \
	-e AWS_S3_KEY_PREFIX_STATIC
DOCKER_RUN_DEV_OPTS := $(DEV_ENVS) $(DEV_MOUNT) "$(DEV_IMAGE)"
DOCKER_RUN_DEV := docker run $(if $(DOCKER_NON_INTERACTIVE), , -it) $(DOCKER_RUN_DEV_OPTS)
DOCKER_RUN_DEV_NOTTY := docker run $(if $(DOCKER_NON_INTERACTIVE), , -i) $(DOCKER_RUN_DEV_OPTS)

DEPLOY_MOUNT := -v "$(CURDIR)/$(BUILD_BIND_DIR):/$(BUILD_BIND_DIR)"
DOCKER_RUN_DEPLOY_OPTS := \
	-e AWS_ACCESS_KEY_ID \
	-e AWS_SECRET_ACCESS_KEY \
	$(DEPLOY_MOUNT) "$(DEPLOY_IMAGE)"
DOCKER_RUN_DEPLOY := docker run $(if $(DOCKER_NON_INTERACTIVE), , -it) $(DOCKER_RUN_DEPLOY_OPTS)
DOCKER_RUN_DEPLOY_NOTTY := docker run $(if $(DOCKER_NON_INTERACTIVE), , -i) $(DOCKER_RUN_DEPLOY_OPTS)

PRE_BUILD_TARGET ?= build-build-image
PRE_DEV_TARGET ?= build-dev-image
PRE_DEPLOY_TARGET ?= build-dep-image

default: app

## Build Dev Docker image
build-build-image: dist
	docker build -t "$(BUILD_IMAGE)" -f build.Dockerfile .

## Build Dev Docker image
build-dev-image:
	DOCKER_BUILDKIT=1 docker build -t "$(DEV_IMAGE)" -f dev.Dockerfile .

## Build Deploy Docker image
build-dep-image:
	docker build -t "$(DEPLOY_IMAGE)" -f dep.Dockerfile .

## Create the "dist" directory
dist:
	mkdir -p dist

## Create .pyc only distribution
app: $(PRE_BUILD_TARGET)
	$(if $(PRE_BUILD_TARGET),$(DOCKER_RUN_BUILD)) python ./script/build.py exammanagement/ \
	--requirements requirements/base.txt -o dist/app.pyz --main manage:main \
	--include *.mo *.html *.txt *.txt.gz *.json pytz/* *.pyc *.so* *.pyd* *METADATA *.scss \
	--exclude boto3/* botocore/* -q --compress --collect_manifest

## Run dev server
up:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up -d --build

# Logs for web container
logs:
	docker-compose logs -f web

# Logs for db container
logs-db:
	docker-compose logs -f db

down:
	docker-compose down

migrate:
	docker-compose exec web python exammanagement/manage.py migrate

rollback:
	docker-compose exec web python exammanagement/manage.py migrate main $(name)

make_migrations:
	docker-compose exec web python exammanagement/manage.py makemigrations

show_migrations:
	docker-compose exec web python exammanagement/manage.py showmigrations

merge_migrations:
	docker-compose exec web python exammanagement/manage.py makemigrations --merge

seed_migrations:
	docker-compose exec web python exammanagement/manage.py makemigrations --empty main --name $(name)

createsuperuser:
	docker-compose exec web python exammanagement/manage.py createsuperuser

translate: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) python exammanagement/manage.py makemessages -l vi -l en

test: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) python exammanagement/manage.py test

lint: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) pre-commit run --all-files

## Generate requirements files
requirements: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) ./script/requirements.sh

collectstatic: $(PRE_DEV_TARGET)
	$(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) python exammanagement/manage.py compilescss \
		&& $(if $(PRE_DEV_TARGET),$(DOCKER_RUN_DEV)) python exammanagement/manage.py collectstatic --noinput --ignore=*.scss

deletestatic: $(PRE_DEPLOY_TARGET)
	$(if $(PRE_DEPLOY_TARGET),$(DOCKER_RUN_DEPLOY)) python /script/deletestatic.py "$(AWS_S3_BUCKET_NAME_STATIC)" "$(DEPLOYMENT_STAGE_NAME)"

deploy: $(PRE_DEPLOY_TARGET)
	$(if $(PRE_DEPLOY_TARGET),$(DOCKER_RUN_DEPLOY)) python /script/deploy.py "$(AWS_S3_BUCKET_NAME_DEPLOY)" "$(DEPLOYMENT_STAGE_NAME)" --dist dist/app.pyz

deploy-destroy: $(PRE_DEPLOY_TARGET)
	$(if $(PRE_DEPLOY_TARGET),$(DOCKER_RUN_DEPLOY)) python /script/deploy.py "$(AWS_S3_BUCKET_NAME_DEPLOY)" "$(DEPLOYMENT_STAGE_NAME)" --destroy

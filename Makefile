PROJECT := dongdong
TAG ?= latest
IMAGE := ${PROJECT}:${TAG}

deps:
	pip install -U poetry
	poetry config virtualenvs.in-project true
	poetry install

prod-deps:
	pip install -U poetry
	poetry config virtualenvs.create false
	poetry install --no-dev --no-interaction --no-ansi

build:
	docker build \
		--file devops/Dockerfile \
		--tag ${IMAGE} \
		.

run:
	poetry run python ${PROJECT}

prod-run:
	build
	docker compose \
		--file devops/docker-compose.yaml \
		up -d


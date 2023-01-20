PROJECT := dongdong
TAG ?= latest
IMAGE := ${PROJECT}:${TAG}

install:
	pip install --upgrade pip 
	pip install -r requirements.txt

build:
	docker build \
		--file devops/Dockerfile \
		--tag ${IMAGE} \
		.

run:
	python ${PROJECT}

prod-run:
	build
	docker compose \
		--file devops/docker-compose.yaml \
		up -d


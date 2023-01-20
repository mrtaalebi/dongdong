PROJECT := dongdong
TAG ?= latest
IMAGE := ${PROJECT}:${TAG}

install:
	pip install --upgrade pip 
	pip install -r requirements.txt

build:
	docker build --tag ${IMAGE} .

run:
	python ${PROJECT}

prod-run:
	docker compose up -d


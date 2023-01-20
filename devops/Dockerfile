FROM python:3.9-alpine

ENV TZ Asia/Tehran

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN make prod-deps

ENTRYPOINT ["make", "run"]

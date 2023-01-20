FROM python:3.11-alpine

ENV TZ Asia/Tehran

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN apk add build-base --no-cache
RUN make prod-deps

ENTRYPOINT ["make", "run"]

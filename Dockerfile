FROM python:3.11-alpine

ENV TZ Asia/Tehran

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN apk add make --no-cache
RUN make install

ENTRYPOINT ["make", "run"]

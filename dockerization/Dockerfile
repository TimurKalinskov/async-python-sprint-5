FROM python:3.11.1-alpine3.17

RUN apk add gcc g++ musl-dev rust cargo patchelf && pip install --upgrade pip

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/src/

COPY requirements.txt /usr/src/app/src/
RUN pip install -r requirements.txt

COPY ./src/ /usr/src/app/src/

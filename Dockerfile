FROM python:3.7.10-buster

WORKDIR /app

ADD . .

RUN pip install --no-cache-dir -r ./requirements.txt && chown -R 1001:1001 *

RUN useradd -u 1001 app

USER 1001

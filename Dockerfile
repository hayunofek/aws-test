FROM python:3.7.10-buster

WORKDIR /app

ADD app/ .

RUN pip install --no-cache-dir -r ./requirements.txt && chown -R 1001:1001 *

RUN useradd -u 1001 app

USER 1001
EXPOSE 8080

ENTRYPOINT ["python3", "./db_utils.py"]

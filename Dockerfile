FROM python:3.7.10-buster

WORKDIR /app

ADD app/ .

RUN pip install --no-cache-dir -r ./requirements.txt && chown -R 1001:1001 *

RUN useradd -u 1001 app

ENV FLASK_APP=book_manager

USER 1001

EXPOSE 5000

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]

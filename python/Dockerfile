FROM python:3.8-slim-buster

WORKDIR /app

USER root

COPY python/requirements.txt .

RUN pip install -r requirements.txt

COPY python/* .
COPY db/* db/

EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]

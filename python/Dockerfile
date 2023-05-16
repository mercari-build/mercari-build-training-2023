FROM python:3.8

WORKDIR /app

USER root

COPY python/requirements.txt .

RUN pip install -r requirements.txt

COPY python .
COPY db/mercari.sqlite3 .

EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
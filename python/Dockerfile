FROM python:3.10.11-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari

WORKDIR /home/trainee
COPY db db
COPY python python

RUN apk update \
    && apk add --no-cache sqlite
RUN sqlite3 db/mercari.sqlite3 < db/items.db

WORKDIR /home/trainee/python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
ENV PATH $PATH:/home/trainee/.local/bin

RUN chown -R trainee:mercari /home/trainee/db \
    && chown -R trainee:mercari /home/trainee/python/images
USER trainee

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]

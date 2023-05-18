FROM alpine

WORKDIR /app
COPY requirements.txt requirements.txt
RUN apk add --no-cache python3 python3-dev py3-pip && pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .

RUN addgroup -S mercari && adduser -S trainee -G mercari
# RUN chown -R trainee:mercari /path/to/db

USER trainee

CMD ["python3", "-V"]

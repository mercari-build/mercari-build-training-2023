FROM golang:1.20.2-alpine

WORKDIR /project

COPY go.mod go.sum ./
COPY app ./app/

RUN addgroup -S mercari && adduser -S trainee -G mercari
RUN chown -R trainee:mercari /project/app

ENV GOOS=linux
ENV GOARCH=amd64
ENV CGO_ENABLED=1

RUN apk add --no-cache git sqlite-dev gcc musl-dev
RUN go mod download

USER trainee

WORKDIR /project/app

# complie the application
RUN go build -o main
EXPOSE 9000

CMD ["go", "version"]
CMD ["./main"]

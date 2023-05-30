FROM node:16-alpine
WORKDIR /app

COPY *.json ./
COPY /src/ ./src
COPY /public/ ./public

RUN addgroup -S mercari && adduser -S trainee -G mercari
RUN npm ci

EXPOSE 3000

CMD ["npm", "start"]

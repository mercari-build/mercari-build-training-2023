FROM node:16-alpine

WORKDIR /app

USER root

# COPY package.json package-lock.json tsconfig.json ./

COPY package.json package-lock.json tsconfig.json ./
COPY public public
COPY src src

RUN npm ci

# RUN mkdir node_modules/.cache && chown -R trainee:mercari node_modules/.cache

EXPOSE 3000

CMD ["npm", "start"]

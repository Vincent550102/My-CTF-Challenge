FROM node:17-alpine

RUN apk update && apk upgrade && apk add chromium

WORKDIR /app
COPY package.json yarn.lock /app/
RUN yarn

COPY . .

ENTRYPOINT ["yarn", "start"]

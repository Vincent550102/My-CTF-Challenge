FROM node:17-alpine

RUN apk update && apk upgrade && apk add chromium

WORKDIR /app
COPY package.json yarn.lock /app/
RUN yarn

COPY . .

# prevent navigation to other pages to leak the flag
COPY policy.json /etc/chromium/policies/managed/policy.json

ENTRYPOINT ["yarn", "start"]

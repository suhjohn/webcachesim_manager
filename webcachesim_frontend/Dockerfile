FROM node:11 AS builder
WORKDIR /app
COPY package.json .
RUN yarn install
COPY . .
RUN yarn build && yarn --production

FROM node:11
WORKDIR /app
COPY --from=builder /app .
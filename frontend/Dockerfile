FROM node:20-alpine AS builder

WORKDIR /usr/app

COPY package.json package-lock.json ./

RUN npm install
COPY . .
RUN npm run build --prod

FROM nginx:1.25.4-alpine

COPY --from=builder /usr/app/dist/frontend/browser/ /usr/share/nginx/html
EXPOSE 80

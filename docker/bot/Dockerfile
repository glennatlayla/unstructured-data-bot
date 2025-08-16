FROM node:18-alpine

WORKDIR /app

COPY services/bot/package.json .
RUN npm install

COPY services/bot/ .

EXPOSE 3978

CMD ["npm", "start"]

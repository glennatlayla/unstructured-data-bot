FROM node:18-alpine

WORKDIR /app

COPY services/admin-ui/package.json .
RUN npm install

COPY services/admin-ui/ .

EXPOSE 3000

CMD ["npm", "start"]

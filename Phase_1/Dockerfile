FROM node:14

RUN apt-get update

ENV HOME /root

RUN apt-get updsate --fix-missing
COPY . .

RUN npm install express
RUN npm install express-formidable
RUN npm install socket.io

EXPOSE 8000 

CMD node server.js
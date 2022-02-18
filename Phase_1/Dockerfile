FROM node:14

RUN apt-get update

ENV HOME /root

RUN apt-get update --fix-missing
COPY . .

RUN npm install express
RUN npm install express-formidable
RUN npm install socket.io
RUN npm install mongodb
EXPOSE 3000

CMD node server.js

#pass env variable to container
#https://www.cloudsavvyit.com/14081/how-to-pass-environment-variables-to-docker-containers/

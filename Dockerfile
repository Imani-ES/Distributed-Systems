FROM node:14

RUN apt-get update

ENV HOME /root

RUN apt-get updsate --fix-missing
COPY . .
RUN npm install #install dependencies

EXPOSE 8000 

CMD #Runs command after container made
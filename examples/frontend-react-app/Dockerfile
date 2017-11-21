FROM node:8.9.1

ENV NPM_CONFIG_LOGLEVEL warn
ENV APP_CODE /app

RUN mkdir $APP_CODE
ADD . $APP_CODE
WORKDIR $APP_CODE

RUN npm install
RUN npm install -g serve

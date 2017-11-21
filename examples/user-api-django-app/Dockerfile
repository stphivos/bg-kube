FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV APP_CODE /src

RUN mkdir $APP_CODE
ADD . $APP_CODE

RUN pip install -r $APP_CODE/requirements.txt

WORKDIR $APP_CODE

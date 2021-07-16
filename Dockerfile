# pull official base image
FROM python:3.7.9-alpine

# set work directory
WORKDIR /usr/src/ControlString_co

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements_windows.txt .

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev

RUN pip install -r requirements_windows.txt


RUN apk del .tmp-build-deps

RUN mkdir /ControlString_co
WORKDIR /ControlString_co
COPY ./ControlString_co /ControlString_co

RUN adduser -D user

USER user

# copy project
COPY . .
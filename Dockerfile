FROM python:3.9.5-slim-buster
LABEL maintainer="Sreenath Sasidharan Nair sreenath@ebi.ac.uk"

# RUN apk add git gcc
# RUN apk add --no-cache  git g++ python3-dev && \
#     pip3 install --upgrade pip setuptools

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
COPY ./logging.conf .
RUN pip3 install -r requirements.txt

# copy the project
COPY . .

# EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:8000 --conf /app/app/gunicorn_conf.py app.app:app

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8
LABEL maintainer="Sreenath Sasidharan Nair sreenath@ebi.ac.uk"

RUN apk add git gcc
RUN apk add --no-cache  git g++ python3-dev && \
    pip3 install --upgrade pip setuptools

ADD requirements.txt /app/
ADD logging.conf /app/
RUN pip3 install -r requirements.txt
ADD /app /app/app
WORKDIR /app

EXPOSE 8000
CMD uvicorn app.app:app --host 0.0.0.0 --port 8000 --root-path $ROOT_PATH

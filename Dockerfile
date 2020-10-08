FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8
LABEL maintainer="Sreenath Sasidharan Nair sreenath@ebi.ac.uk"

RUN apk add git

ADD requirements.txt /app/
ADD logging.conf /app/
ADD stub.json /app/
RUN pip install -r requirements.txt
ADD /app /app/app
WORKDIR /app

EXPOSE 80
CMD uvicorn app.app:app --host 0.0.0.0 --port 80

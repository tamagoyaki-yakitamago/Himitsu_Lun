# Python
FROM python:3.7-alpine

# Setting environment variable
ENV PYTHONUNBUFFERED 1

# Create and set work directory
RUN mkdir /code
WORKDIR /code

# Copy requirements.txt and install
ADD requirements.txt /code/
RUN apk update && \
    apk add postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    build-base \
    linux-headers 
# RUN pip install -r requirements.txt

# Copy directory
ADD . /code/

RUN pip install pipenv
RUN pipenv --python 3.7
RUN pipenv sync
# syntax=docker/dockerfile:1
# Base image
FROM python:3.8 as base
RUN apt-get update && apt-get -y install cmake make gcc g++ golang python2.7-dev
RUN pip install -U pip==20.0.2

# Download Python dependencies
FROM base as python-components
ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS
ARG DIR
RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/testjfrog-pypi/simple
COPY requirements.txt requirements.txt
RUN pip download -r requirements.txt -d /vendor/python
# Custom package
COPY dnp3/src /code
WORKDIR /code
RUN pip download -r requirements.txt -d /vendor/python
RUN python setup.py bdist_wheel --dist-dir /vendor/python_custom

# Build image
FROM base as runtime
ARG DIR
# Install python dependencies
COPY --from=python-components /vendor/python /vendor/python
COPY --from=python-components /vendor/python_custom /vendor/python_custom
RUN pip install /vendor/python/*
RUN pip install /vendor/python_custom/*

# Install binaries (python)
WORKDIR /code
COPY $DIR/bin /usr/bin

# Copy management code
COPY management /code/management
# COPY runner.py  /code
WORKDIR /code/management

ENTRYPOINT ["python3", "network.py"]

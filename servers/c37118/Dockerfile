# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as c37118-stage

# Custom package
COPY c37118 /opt/c37118
WORKDIR /opt/c37118/
RUN pip download -r requirements.txt -d /opt/c37118/python

CMD ["tail", "-f", "/dev/null"]


FROM python:3.8-slim as base
RUN apt update && apt -y install libpq-dev gcc cmake make g++ python2.7-dev

# Download Python dependencies
FROM base as python-stage
COPY requirements.txt requirements.txt
RUN pip download -r requirements.txt -d /vendor/python

# Build image
FROM base as runtime
# Install python dependencies
COPY --from=python-stage /vendor/python /vendor/python
RUN pip install /vendor/python/*
RUN rm -fr /vendor/python

# Copy management code
COPY management /opt/management
COPY management/openvpn-ns /usr/bin

# C37118
COPY --from=c37118-stage /opt/c37118 /opt/c37118
RUN /opt/c37118/install.sh

# COPY runner.py  /code
WORKDIR /opt/management

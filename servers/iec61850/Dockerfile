# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as iec61850-stage
RUN apt-get update && apt-get -y install make gcc

# Custom package
COPY iec61850 /opt/iec61850
WORKDIR /opt/iec61850/src
RUN make

CMD ["tail", "-f", "/dev/null"]

# Base image
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

# IEC61850
COPY --from=iec61850-stage /opt/iec61850 /opt/iec61850
RUN /opt/iec61850/install.sh

# COPY runner.py  /code
WORKDIR /opt/management

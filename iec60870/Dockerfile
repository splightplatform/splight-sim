# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as iec60870-stage
RUN apt-get update && apt-get -y install cmake make gcc g++

# Custom package
COPY iec60870 /opt/iec60870
WORKDIR /opt/iec60870/src
RUN make || make # The double pipe fix something

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

# IEC60870
COPY --from=iec60870-stage /opt/iec60870 /opt/iec60870
RUN /opt/iec60870/install.sh

# COPY runner.py  /code
WORKDIR /opt/management

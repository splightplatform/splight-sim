# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as dnp3-stage
RUN apt-get update && apt-get -y install cmake make gcc g++ python2.7-dev

# Custom package
COPY dnp3 /opt/dnp3
WORKDIR /opt/dnp3/src
RUN pip download -r requirements.txt -d /opt/dnp3/python
RUN python setup.py bdist_wheel --dist-dir /opt/dnp3/python_custom

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

# DNP3
COPY --from=dnp3-stage /opt/dnp3 /opt/dnp3
RUN /opt/dnp3/install.sh

# COPY runner.py  /code
WORKDIR /opt/management

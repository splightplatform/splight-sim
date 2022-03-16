# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as iec61850-stage
RUN apt-get update && apt-get -y install make gcc

# Custom package
COPY iec61850 /opt/iec61850
WORKDIR /opt/iec61850/src
RUN make

CMD ["tail", "-f", "/dev/null"]

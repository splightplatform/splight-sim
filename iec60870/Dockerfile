# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as iec60870-stage
RUN apt-get update && apt-get -y install cmake make gcc g++

# Custom package
COPY iec60870 /opt/iec60870
WORKDIR /opt/iec60870/src
RUN make || make # The double pipe fix something

CMD ["tail", "-f", "/dev/null"]

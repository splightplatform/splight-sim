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

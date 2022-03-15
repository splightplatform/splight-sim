# syntax=docker/dockerfile:1
# Base image
FROM python:3.8-slim as c37118-stage

# Custom package
COPY c37118 /opt/c37118
WORKDIR /opt/c37118/
RUN pip download -r requirements.txt -d /opt/c37118/python

CMD ["tail", "-f", "/dev/null"]

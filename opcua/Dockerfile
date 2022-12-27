FROM python:3.8

RUN mkdir /src
COPY ./requirements.txt /src/requirements.txt
COPY ./opcua_server.py /src/opcua_server.py

RUN pip install -r /src/requirements.txt

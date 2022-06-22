FROM python:3.8

RUN mkdir /src
COPY ./requirements.txt /src/requirements.txt
COPY ./random_publisher.py /src/random_publisher.py
COPY ./csv_publisher.py /src/csv_publisher.py

RUN pip install -r /src/requirements.txt
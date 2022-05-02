FROM python:3.8

RUN mkdir /src
COPY ./requirements.txt /src/requirements.txt
COPY ./publisher.py /src/publisher.py

RUN pip install -r /src/requirements.txt
CMD ["python", "/src/publisher.py"]
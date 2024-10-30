FROM python:3.8

RUN mkdir /src
ADD requirements.txt /src/
RUN pip install -r /src/requirements.txt

ADD . /src/
WORKDIR /src/

CMD ["python", "/src/main.py"]
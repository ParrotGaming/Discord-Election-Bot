FROM python:3.8.1-slim-buster

WORKDIR /usr/src/app
RUN pip install --upgrade pip

COPY /bot .

RUN pip install -r requirements.txt

CMD python3 main.py
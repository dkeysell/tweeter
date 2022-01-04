# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./tweeter/app.py .

RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader stopwords

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0" ]
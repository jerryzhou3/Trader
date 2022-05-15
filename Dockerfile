FROM python:3.9.0-slim-buster
ADD . .
RUN pip install -r requirements.txt

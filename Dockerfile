# syntax=docker/dockerfile:1
FROM python:3.7
ENV PYTHONUNBUFFERED=1
WORKDIR /restaurant
COPY requirements.txt /restaurant/
RUN pip install -r requirements.txt
COPY . /restaurant/
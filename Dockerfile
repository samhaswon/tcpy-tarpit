FROM python:3-alpine

ENV PYTHONUNBUFFERED=TRUE
LABEL authors="samue"

WORKDIR /usr/src/app
COPY . .

ENTRYPOINT ["top", "-b"]
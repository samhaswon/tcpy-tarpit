FROM python:3-alpine

LABEL authors="Samuel Howard"
ENV PYTHONUNBUFFERED=TRUE
ENV TCP_NODELAY=1
ENV TCP_QUICKACK=1

EXPOSE 8080
EXPOSE 8081

WORKDIR /usr/src/app
RUN pip install --no-cache-dir prometheus-client && \
    pip install --no-cache-dir uvloop || echo "Not using uvloop"

COPY . .

ENTRYPOINT [ "/usr/src/app/main.py" ]
STOPSIGNAL SIGKILL

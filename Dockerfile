FROM python:3-alpine

LABEL authors="Samuel Howard"
ENV PYTHONUNBUFFERED=TRUE
ENV TCP_NODELAY=1
ENV TCP_QUICKACK=1

WORKDIR /usr/src/app
COPY . .

ENTRYPOINT [ "/usr/src/app/main.py" ]
STOPSIGNAL SIGKILL
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 CMD test -f /usr/src/app/alive.txt && rm /usr/src/app/alive.txt && echo "Healthy" || echo "Unhealthy"

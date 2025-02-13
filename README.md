# tcpy-tarpit

A TCP tarpit, written in Python, that responds with something resembling HTTP.

## How It Works

Here's what the server responds with first:

```
HTTP/1.1 200 OK\r\n
Content-Type: application/x-binary\r\n
Transfer-Encoding: chunked\r\n
\r\n
```

Then, it uses TCP streaming to respond with more data until the client disconnects.

## Supported Architectures
| Architecture | Available | Tag    |
|:------------:|:---------:|--------|
|    x86-64    |     ✅     | latest |
|   arm64v8    |     ✅     | latest |
|   arm32v7    |     ✅     | latest |
|   arm32v6    |     ✅     | latest |
|     i386     |     ✅     | latest |

# Setup

You have the choice of the following modes:

- `mist` mist a byte every 10 seconds. 
- `drip` drips 128 B response chunks every second.
- `trickle` trickles 1 kiB response chunks every half-second.
- `flood` sends 1024 kiB response chunks as fast as possible.

## Without Logging

### Docker run
```shell
docker run -d -p 8080:8080 \
       --restart=unless-stopped \
       --name tcpy-tarpit \
       -e MODE=drip \
       samhaswon/tcpy-tarpit
```

### Docker Compose
```yml
services:
  tcpy-tarpit:
    image: samhaswon/tcpy-tarpit
    container_name: tcpy-tarpit
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - TZ=America/New_York  # your linux timezone
      - MODE=drip
```

## With Logging

Included in this repository, there is a sample [prometheus configuration](./prometheus.yml),
along with a basic [Grafana dashboard](./tcpy-tarpit-1739424908859.json).

You should adjust these as needed or as required.
The following docker compose configuration uses folders rather than volumes if that matters to you.

```yml
services:
  tcpy-tarpit:
    image: samhaswon/tcpy-tarpit
    container_name: tcpy-tarpit
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "8081:8081"
    environment:
      - TZ=America/New_York  # your linux timezone
      - MODE=drip
  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./grafana:/var/lib/grafana
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --storage.tsdb.retention.time=45d
      - --web.console.libraries=/usr/share/prometheus/console_libraries
      - --web.console.templates=/usr/share/prometheus/consoles
      - --web.enable-admin-api
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus:/prometheus

```

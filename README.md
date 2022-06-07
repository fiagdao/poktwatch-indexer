# POKTwatch

An easy to use Python and Postgres indexer for Pocket Network

## Installation

```
git clone https://github.com/fiagdao/poktwatch-indexer.git
cd poktwatch-indexer
docker-compose up -d
```

## Requirements

1. Docker and docker-compose
2. A server with more than 4 CPU's (to run it fast)


## Usage

If you do not want to run your own indexer, there is a free one available at https://api.pokt.watch

### PostgREST

A (PostGREST)[https://postgrest.org/en/stable/] endpoint at 0.0.0.0:3000 is exposed.

You can connect this with other sites such as the (POKTwatch-frontend)[https://github.com/fiagdao/poktwatch-frontend], or create your own API's

### Postgres

A postgres database is exposed at 0.0.0.0:5432. The credentials are specified in the .env file.

### Pocket

If you do not want to wait for your pocket node to fully sync, you can download a snapshot and put it in the data/pocket folder.

# Redis Cache

A small Redis-like cache server built with Python sockets.

This project is mainly for learning how an in-memory cache works under the hood. It supports simple text values, binary file storage, key expiry, and LRU eviction when the cache reaches its memory limit.

## What It Can Do

- Store and read text values with `SET` and `GET`
- Delete keys with `DEL`
- Check the server with `PING`
- Set expiry time with `EXPIRE`
- Upload and download files through the client
- Remove expired keys in the background
- Evict least recently used keys when memory is full

## Project Structure

```text
redis-cache/
|-- server.py              # Starts the cache server
|-- client.py              # Interactive TCP client
|-- test.py                # Simple local command tester
|-- cache/                 # Cache storage, nodes, and LRU logic
|-- commands/              # Command handlers
|-- network/               # TCP server and client handling
|-- protocol/              # Command parser and command model
`-- scheduler/             # Background expiry cleaner
```

## Requirements

Python 3 is required. There are no external dependencies right now, so `requirements.txt` is empty.

## How To Run

Start the cache server:

```bash
python server.py
```

By default, the server runs on:

```text
127.0.0.1:6379
```

In another terminal, start the interactive client:

```bash
python client.py
```

## Commands

### Check Server

```text
PING
```

Response:

```text
PONG
```

### Store A Value

```text
SET name Alice
```

Response:

```text
OK
```

### Read A Value

```text
GET name
```

Response:

```text
Alice
```

If the key does not exist:

```text
NULL
```

### Delete A Key

```text
DEL name
```

Response:

```text
OK
```

If the key does not exist:

```text
NOT FOUND
```

### Expire A Key

```text
EXPIRE name 10
```

This makes `name` expire after 10 seconds.

Response:

```text
1
```

If the key does not exist:

```text
0
```

## File Upload And Download

The interactive client has friendly commands for files.

Upload a file:

```text
upload photo C:\path\to\photo.jpg
```

Download a file:

```text
download photo C:\path\to\saved-photo.jpg
```

Internally, the server uses:

```text
SET_FILE <key> <file_size>
GET_FILE <key>
```

Use `GET_FILE` for binary data. Normal `GET` is only for text values.

## How It Works

The server keeps all values in memory. Each key points to a cache node that stores the value, size, data type, and optional expiry time.

When a key is read or updated, it is moved to the front of the LRU list. If the cache goes over the memory limit, the least recently used keys are removed first.

Expired keys are cleaned up by a background thread, and they are also removed when accessed after expiry.

## Memory Limit

The cache is currently limited to 100 MB.

You can change this in `network/server.py`:

```python
self.storage = CacheStorage(
    max_memory=100 * 1024 * 1024
)
```

## Quick Local Test

You can also test commands without opening a network connection:

```bash
python test.py
```

Then type commands like:

```text
SET city Delhi
GET city
EXPIRE city 5
DEL city
exit
```

## Notes

- Data is stored only in memory.
- Data is lost when the server stops.
- The server is built for learning and experimentation, not production use.

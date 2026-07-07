"""
Application entry point.

Starts the cache server.
"""

from network.server import CacheServer


def main():

    server = CacheServer(
        host="127.0.0.1",
        port=6379
    )

    server.start()


if __name__ == "__main__":
    main()
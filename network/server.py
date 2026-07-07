"""
TCP server for the cache.
"""

import socket
import threading

from cache.storage import CacheStorage
from commands.dispatcher import CommandDispatcher
from network.client_handler import handle_client
from scheduler.cleaner import cleaner_worker


class CacheServer:

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6379
    ):

        self.host = host
        self.port = port

        self.running = True

        self.server_socket = None

        # Shared cache
        self.storage = CacheStorage(
            max_memory=100 * 1024 * 1024
        )

        # Dispatcher
        self.dispatcher = CommandDispatcher(
            self.storage
        )


    def stop(self):

        self.running = False

        print("Stopping cache server...")


    def start(self):

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind(
            (self.host, self.port)
        )

        self.server_socket.listen()

        self.server_socket.settimeout(1)


        print(
            f"Cache Server started on {self.host}:{self.port}"
        )

        print("Press Ctrl+C to stop.")


        # -------------------------
        # Start TTL Cleaner
        # -------------------------

        cleaner_thread = threading.Thread(
            target=cleaner_worker,
            args=(
                self.storage,
                lambda: self.running
            ),
            daemon=True
        )

        cleaner_thread.start()


        try:

            while self.running:

                try:

                    client_socket, address = (
                        self.server_socket.accept()
                    )

                except socket.timeout:

                    continue


                print(
                    f"Client connected: {address}"
                )


                thread = threading.Thread(
                    target=handle_client,
                    args=(
                        client_socket,
                        self.dispatcher
                    ),
                    daemon=True
                )

                thread.start()


        except KeyboardInterrupt:

            print("\nStopping Server...")

            self.stop()


        finally:

            if self.server_socket:

                self.server_socket.close()


            print("Server stopped.")
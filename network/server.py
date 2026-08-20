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
        port: int = 6379,
    ):
        self.host = host
        self.port = port

        self.running = False
        self.server_socket = None

        self.storage = CacheStorage(
            max_memory=100 * 1024 * 1024
        )

        self.dispatcher = CommandDispatcher(
            self.storage
        )

        self.cleaner_thread = None
        self.client_sockets = set()
        self.clients_lock = threading.Lock()

    def stop(self):

        if not self.running:
            return

        self.running = False

        print("Stopping cache server...")

        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except OSError:
                pass

        with self.clients_lock:
            clients = list(self.client_sockets)

        for client_socket in clients:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                client_socket.close()
            except OSError:
                pass

    def start(self):

        self.running = True

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
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

        self.cleaner_thread = threading.Thread(
            target=cleaner_worker,
            args=(
                self.storage,
                lambda: self.running,
            ),
            daemon=False,
        )

        self.cleaner_thread.start()

        try:

            while self.running:

                try:
                    client_socket, address = (
                        self.server_socket.accept()
                    )

                except socket.timeout:
                    continue

                except OSError:
                    if not self.running:
                        break

                    raise

                client_socket.settimeout(30)

                with self.clients_lock:
                    self.client_sockets.add(client_socket)

                print(
                    f"Client connected: {address}"
                )

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(
                        client_socket,
                    ),
                    daemon=True,
                )

                thread.start()

        except KeyboardInterrupt:

            print("\nStopping Server...")

        finally:

            self.stop()

            if self.cleaner_thread is not None:
                self.cleaner_thread.join(timeout=5)

            print("Server stopped.")

    def _handle_client(
        self,
        client_socket: socket.socket,
    ):

        try:
            handle_client(
                client_socket,
                self.dispatcher,
            )

        finally:
            with self.clients_lock:
                self.client_sockets.discard(
                    client_socket
                )
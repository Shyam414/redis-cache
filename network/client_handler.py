"""
Handles one connected client.

Protocol:

PING

SET name Shyam

GET name

DEL name

SET_FILE photo 245678
<245678 raw bytes>

GET_FILE photo
"""

from socket import socket

from protocol.parser import Parser
from commands.dispatcher import CommandDispatcher


def handle_client(
    client_socket: socket,
    dispatcher: CommandDispatcher
):

    # Treat socket like a binary file
    reader = client_socket.makefile("rb")
    writer = client_socket.makefile("wb")

    try:

        while True:

            # -------------------------
            # Read one command line
            # -------------------------

            header = reader.readline()

            if not header:
                break

            request = header.decode("utf-8").strip()

            print("Request:", request)

            try:

                command = Parser.parse(request)

                # -------------------------
                # Receive file
                # -------------------------

                if command.command == "SET_FILE":

                    print(
                        f"Receiving {command.file_size} bytes..."
                    )

                    command.value = reader.read(
                        command.file_size
                    )

                    if len(command.value) != command.file_size:

                        raise ValueError(
                            "Incomplete file received."
                        )

                # -------------------------
                # Execute command
                # -------------------------

                response = dispatcher.dispatch(command)

                # -------------------------
                # Sending file
                # -------------------------

                if command.command == "GET_FILE":

                    if response is None:

                        writer.write(b"NULL\n")

                    else:

                        writer.write(
                            f"{len(response)}\n".encode()
                        )

                        writer.write(response)

                    writer.flush()

                    continue

                # -------------------------
                # Normal response
                # -------------------------

                if isinstance(response, bytes):

                    writer.write(response + b"\n")

                else:

                    writer.write(
                        str(response).encode() + b"\n"
                    )

                writer.flush()

            except Exception as e:

                writer.write(
                    f"ERROR: {e}\n".encode()
                )

                writer.flush()

    except Exception as e:

        print(e)

    finally:

        print("Client disconnected")

        try:
            writer.close()
        except Exception:
            pass

        try:
            reader.close()
        except Exception:
            pass

        try:
            client_socket.close()
        except Exception:
            pass
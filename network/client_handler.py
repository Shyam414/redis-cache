from socket import socket

from protocol.parser import Parser
from commands.dispatcher import CommandDispatcher


MAX_HEADER_SIZE = 4096
MAX_FILE_SIZE = 10 * 1024 * 1024


def handle_client(
    client_socket: socket,
    dispatcher: CommandDispatcher,
):

    reader = client_socket.makefile("rb")
    writer = client_socket.makefile("wb")

    try:

        while True:

            # Read command header

            header = reader.readline(
                MAX_HEADER_SIZE + 1
            )

            if not header:
                break

            # Validate header size

            if len(header) > MAX_HEADER_SIZE:

                writer.write(
                    b"ERROR: Command too large\n"
                )

                writer.flush()
                break

            # Validate complete line

            if not header.endswith(b"\n"):

                writer.write(
                    b"ERROR: Invalid command format\n"
                )

                writer.flush()
                break

            # Decode command

            try:

                request = header.decode(
                    "utf-8"
                ).strip()

            except UnicodeDecodeError:

                writer.write(
                    b"ERROR: Invalid UTF-8 command\n"
                )

                writer.flush()
                continue

            # Parse and execute command

            try:

                command = Parser.parse(
                    request
                )

                # Receive file

                if command.command == "SET_FILE":

                    if command.file_size is None:

                        raise ValueError(
                            "Missing file size."
                        )

                    if command.file_size < 0:

                        raise ValueError(
                            "Invalid file size."
                        )

                    if (
                        command.file_size
                        > MAX_FILE_SIZE
                    ):

                        raise ValueError(
                            "File too large."
                        )

                    print(
                        f"Receiving "
                        f"{command.file_size} bytes..."
                    )

                    command.value = reader.read(
                        command.file_size
                    )

                    if (
                        len(command.value)
                        != command.file_size
                    ):

                        raise ValueError(
                            "Incomplete file received."
                        )
                    print("received")

                # Execute command

                response = dispatcher.dispatch(
                    command
                )

                # Send file response

                if command.command == "GET_FILE":

                    if response is None:

                        writer.write(
                            b"NULL\n"
                        )

                    else:

                        writer.write(
                            f"{len(response)}\n"
                            .encode("utf-8")
                        )

                        writer.write(
                            response
                        )

                    writer.flush()
                    continue

                # Send normal response

                if isinstance(response, bytes):

                    writer.write(
                        response + b"\n"
                    )

                else:

                    writer.write(
                        str(response)
                        .encode("utf-8")
                        + b"\n"
                    )

                writer.flush()

            # Expected client errors

            except ValueError as e:

                writer.write(
                    f"ERROR: {e}\n"
                    .encode("utf-8")
                )

                writer.flush()

            # Unexpected server errors

            except Exception as e:

                print(
                    f"Internal error: {e}"
                )

                writer.write(
                    b"ERROR: Internal server error\n"
                )

                writer.flush()

    # Connection errors

    except Exception as e:

        print(
            f"Client connection error: {e}"
        )


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
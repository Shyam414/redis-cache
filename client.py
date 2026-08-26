import os
import socket


HOST = "127.0.0.1"
PORT = 6379

MAX_FILE_SIZE = 10 * 1024 * 1024
SOCKET_TIMEOUT = 30


def recv_exact(
    reader,
    size: int,
) -> bytes:

    if size < 0:
        raise ValueError(
            "Invalid file size"
        )

    if size > MAX_FILE_SIZE:
        raise ValueError(
            "File exceeds maximum allowed size"
        )

    data = bytearray()

    while len(data) < size:

        chunk = reader.read(
            size - len(data)
        )

        if not chunk:
            raise ConnectionError(
                "Server disconnected"
            )

        data.extend(chunk)

    return bytes(data)


def send_line(
    writer,
    text: str,
) -> None:

    writer.write(
        (text + "\n").encode(
            "utf-8"
        )
    )

    writer.flush()


def read_response(
    reader,
) -> str:

    response = reader.readline()

    if not response:
        raise ConnectionError(
            "Server disconnected"
        )

    try:
        return response.decode(
            "utf-8"
        ).strip()

    except UnicodeDecodeError:
        raise ValueError(
            "Invalid UTF-8 response from server"
        )


def main():

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    client.settimeout(
        SOCKET_TIMEOUT
    )

    reader = None
    writer = None

    try:

        client.connect(
            (HOST, PORT)
        )

        reader = client.makefile(
            "rb"
        )

        writer = client.makefile(
            "wb"
        )

        print(
            f"Connected to Cache Server "
            f"({HOST}:{PORT})"
        )

        print()
        print("Commands")
        print("-----------------------------")
        print("PING")
        print("SET <key> <value>")
        print("GET <key>")
        print("DEL <key>")
        print("EXPIRE <key> <ttl>")
        print("upload <key> <file_path>")
        print("download <key> <save_path>")
        print("exit")
        print("-----------------------------")

        while True:

            command = input(
                ">> "
            ).strip()

            if not command:
                continue

            if command.lower() == "exit":
                break

            parts = command.split(
                maxsplit=2
            )

            # -------------------------
            # Upload file
            # -------------------------

            if (
                parts[0].lower()
                == "upload"
            ):

                if len(parts) != 3:

                    print(
                        "Usage: "
                        "upload <key> <file_path>"
                    )

                    continue

                key = parts[1]

                path = parts[2].strip(
                    '"'
                )

                if not os.path.isfile(
                    path
                ):

                    print(
                        "File not found."
                    )

                    continue

                file_size = os.path.getsize(
                    path
                )

                if file_size < 0:

                    print(
                        "Invalid file size."
                    )

                    continue

                if (
                    file_size
                    > MAX_FILE_SIZE
                ):

                    print(
                        "File exceeds maximum "
                        "allowed size."
                    )

                    continue

                # Read file after validation

                with open(
                    path,
                    "rb",
                ) as file:

                    data = file.read()

                # Send file header

                send_line(
                    writer,
                    f"SET_FILE "
                    f"{key} "
                    f"{file_size}",
                )

                # Send raw file bytes

                writer.write(
                    data
                )

                writer.flush()

                response = read_response(
                    reader
                )

                print(
                    response
                )

                continue

            # -------------------------
            # Download file
            # -------------------------

            if (
                parts[0].lower()
                == "download"
            ):

                if len(parts) != 3:

                    print(
                        "Usage: "
                        "download <key> <save_path>"
                    )

                    continue

                key = parts[1]

                save_path = parts[2].strip(
                    '"'
                )

                send_line(
                    writer,
                    f"GET_FILE {key}",
                )

                # Read file size header

                header = read_response(
                    reader
                )

                if header == "NULL":

                    print(
                        "File not found."
                    )

                    continue

                if header.startswith(
                    "ERROR:"
                ):

                    print(
                        header
                    )

                    continue

                try:

                    file_size = int(
                        header
                    )

                except ValueError:

                    print(
                        "Invalid server response: "
                        f"{header}"
                    )

                    break

                if file_size < 0:

                    print(
                        "Invalid file size."
                    )

                    break

                if (
                    file_size
                    > MAX_FILE_SIZE
                ):

                    print(
                        "Server returned a file "
                        "larger than the allowed limit."
                    )

                    break

                # Receive exactly file_size bytes

                file_data = recv_exact(
                    reader,
                    file_size,
                )

                # Save file

                with open(
                    save_path,
                    "wb",
                ) as file:

                    file.write(
                        file_data
                    )

                print(
                    f"Saved to {save_path}"
                )

                continue

            # -------------------------
            # Normal command
            # -------------------------

            send_line(
                writer,
                command,
            )

            response = read_response(
                reader
            )

            print(
                response
            )

    except KeyboardInterrupt:

        print(
            "\nClosing client..."
        )

    except (
        ConnectionError,
        OSError,
        ValueError,
        socket.timeout,
    ) as error:

        print(
            f"Error: {error}"
        )

    finally:

        print(
            "Client disconnected"
        )

        if reader is not None:

            try:
                reader.close()

            except OSError:
                pass

        if writer is not None:

            try:
                writer.close()

            except OSError:
                pass

        try:

            client.shutdown(
                socket.SHUT_RDWR
            )

        except OSError:
            pass

        try:

            client.close()

        except OSError:
            pass


if __name__ == "__main__":
    main()
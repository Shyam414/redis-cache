import os
import socket


HOST = "127.0.0.1"
PORT = 6379


def recv_exact(reader, size):

    if size < 0:
        raise ValueError("Invalid file size")

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


def send_line(writer, text: str):

    writer.write(
        (text + "\n").encode("utf-8")
    )

    writer.flush()


def main():

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    reader = None
    writer = None

    try:

        client.connect((HOST, PORT))

        reader = client.makefile("rb")
        writer = client.makefile("wb")

        print(
            f"Connected to Cache Server ({HOST}:{PORT})"
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

            command = input(">> ").strip()

            if not command:
                continue

            if command.lower() == "exit":
                break

            parts = command.split(maxsplit=2)

            if parts[0].lower() == "upload":

                if len(parts) != 3:
                    print(
                        "Usage: upload <key> <file_path>"
                    )
                    continue

                key = parts[1]
                path = parts[2].strip('"')

                if not os.path.isfile(path):
                    print("File not found.")
                    continue

                with open(path, "rb") as file:
                    data = file.read()

                send_line(
                    writer,
                    f"SET_FILE {key} {len(data)}",
                )

                writer.write(data)
                writer.flush()

                response = reader.readline()

                if not response:
                    raise ConnectionError(
                        "Server disconnected"
                    )

                print(
                    response.decode("utf-8").strip()
                )

                continue

            if parts[0].lower() == "download":

                if len(parts) != 3:
                    print(
                        "Usage: download <key> <save_path>"
                    )
                    continue

                key = parts[1]
                save_path = parts[2].strip('"')

                send_line(
                    writer,
                    f"GET_FILE {key}",
                )

                header = reader.readline()

                if not header:
                    raise ConnectionError(
                        "Server disconnected"
                    )

                header = header.decode(
                    "utf-8"
                ).strip()

                if header == "NULL":
                    print("File not found.")
                    continue

                try:
                    file_size = int(header)
                except ValueError:
                    print(
                        f"Invalid server response: {header}"
                    )
                    continue

                if file_size < 0:
                    print("Invalid file size.")
                    continue

                file_data = recv_exact(
                    reader,
                    file_size,
                )

                with open(save_path, "wb") as file:
                    file.write(file_data)

                print(
                    f"Saved to {save_path}"
                )

                continue

            send_line(
                writer,
                command,
            )

            response = reader.readline()

            if not response:
                raise ConnectionError(
                    "Server disconnected"
                )

            print(
                response.decode("utf-8").strip()
            )

    except KeyboardInterrupt:

        print("\nClosing client...")

    except (
        ConnectionError,
        OSError,
        ValueError,
    ) as error:

        print(f"Error: {error}")

    finally:

        print("Client disconnected")

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
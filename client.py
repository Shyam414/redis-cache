"""
Interactive cache client.
"""

import socket
import os


HOST = "127.0.0.1"
PORT = 6379

def recv_exact(reader, size):

    data = b""

    while len(data) < size:

        chunk = reader.read(
            size - len(data)
        )

        if not chunk:
            raise ConnectionError(
                "Server disconnected"
            )

        data += chunk

    return data

def send_line(writer, text: str):
    writer.write((text + "\n").encode("utf-8"))
    writer.flush()


def main():

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    reader = client.makefile("rb")
    writer = client.makefile("wb")

    print(f"Connected to Cache Server ({HOST}:{PORT})")

    print()
    print("Commands")
    print("-----------------------------")
    print("PING")
    print("SET <key> <value>")
    print("GET <key>")
    print("DEL <key>")
    print("upload <key> <file_path>")
    print("download <key> <save_path>")
    print("exit")
    print("-----------------------------")

    try:

        while True:

            command = input(">> ").strip()

            if not command:
                continue

            if command.lower() == "exit":
                break

            parts = command.split(maxsplit=2)

            # -----------------------------------
            # Upload
            # -----------------------------------

            if parts[0].lower() == "upload":

                if len(parts) != 3:
                    print("Usage: upload <key> <file_path>")
                    continue

                key = parts[1]
                path = parts[2]
                path = path.strip('"')

                if not os.path.exists(path):
                    print("File not found.")
                    continue

                with open(path, "rb") as f:
                    data = f.read()

                send_line(
                    writer,
                    f"SET_FILE {key} {len(data)}"
                )

                writer.write(data)
                writer.flush()

                response = reader.readline().decode().strip()

                print(response)

                continue

            # -----------------------------------
            # Download
            # -----------------------------------

            if parts[0].lower() == "download":

                if len(parts) != 3:
                    print("Usage: download <key> <save_path>")
                    continue

                key = parts[1]
                save_path = parts[2]

                send_line(
                    writer,
                    f"GET_FILE {key}"
                )

                header = reader.readline().decode().strip()

                if header == "NULL":

                    print("File not found.")

                    continue

                file_size = int(header)

                file_data = recv_exact(reader,file_size)

                with open(save_path, "wb") as f:
                    f.write(file_data)

                print(
                    f"Saved to {save_path}"
                )

                continue

            # -----------------------------------
            # Normal Commands
            # -----------------------------------

            send_line(
                writer,
                command
            )

            response = reader.readline()

            print(
                response.decode().strip()
            )

    except KeyboardInterrupt:

        print("\nClosing client...")

    finally:

        print("Client disconnected")

        try:
            reader.close()
        except Exception:
            pass

        try:
            writer.close()
        except Exception:
            pass

        try:
            client.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass

        client.close()

if __name__ == "__main__":
    main()
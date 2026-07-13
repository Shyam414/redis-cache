from protocol.command import Command


class Parser:

    @staticmethod
    def parse(data: str) -> Command:

        data = data.strip()

        if not data:
            raise ValueError("Empty command")

        parts = data.split(maxsplit=2)

        command = parts[0].upper()

        # -----------------------
        # PING
        # -----------------------

        if command == "PING":

            if len(parts) != 1:
                raise ValueError("Usage: PING")

            return Command(
                command="PING"
            )

        # -----------------------
        # GET
        # -----------------------

        elif command == "GET":

            if len(parts) != 2:
                raise ValueError("Usage: GET <key>")

            return Command(
                command="GET",
                key=parts[1]
            )

        # -----------------------
        # DEL
        # -----------------------

        elif command == "DEL":

            if len(parts) != 2:
                raise ValueError("Usage: DEL <key>")

            return Command(
                command="DEL",
                key=parts[1]
            )

        # -----------------------
        # SET
        # -----------------------

        elif command == "SET":

            if len(parts) != 3:
                raise ValueError("Usage: SET <key> <value>")

            return Command(
                command="SET",
                key=parts[1],
                value=parts[2].encode("utf-8")
            )

        # -----------------------
        # SET_FILE
        # -----------------------

        elif command == "SET_FILE":

            if len(parts) != 3:
                raise ValueError(
                    "Usage: SET_FILE <key> <file_size>"
                )

            return Command(
                command="SET_FILE",
                key=parts[1],
                file_size=int(parts[2])
            )
        
        elif command == "GET_FILE":

            if len(parts) != 2:
                raise ValueError(
                    "Usage: GET_FILE <key>"
                )

            return Command(
                command="GET_FILE",
                key=parts[1]
            )

        elif command == "EXPIRE":

            if len(parts) != 3:
                raise ValueError(
                    "Usage: EXPIRE <key> <seconds>"
                )

            return Command(
                command="EXPIRE",
                key=parts[1],
                ttl=int(parts[2])
            )

        else:

            raise ValueError(
                f"Unknown command: {command}"
            )
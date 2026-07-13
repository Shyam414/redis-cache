from cache.storage import CacheStorage
from protocol.command import Command

from commands.set import SetCommand
from commands.get import GetCommand
from commands.delete import DeleteCommand
from commands.ping import PingCommand
from commands.set_file import SetFileCommand
from commands.get_file import GetFileCommand
from commands.expire import ExpireCommand


class CommandDispatcher:

    def __init__(self, storage: CacheStorage):
        self.storage = storage

    def dispatch(self, command: Command):

        if command.command == "SET":
            return SetCommand.execute(
                self.storage,
                command
            )

        elif command.command == "GET":
            return GetCommand.execute(
                self.storage,
                command
            )

        elif command.command == "DEL":
            return DeleteCommand.execute(
                self.storage,
                command
            )

        elif command.command == "PING":
            return PingCommand.execute()
        
        elif command.command == "SET_FILE":

            return SetFileCommand.execute(
                self.storage,
                command
            )

        elif command.command == "GET_FILE":

            return GetFileCommand.execute(
                self.storage,
                command
            )

        elif command.command == "EXPIRE":

            return ExpireCommand.execute(
                self.storage,
                command
            )

        else:
            raise ValueError(
                f"Unsupported command: {command.command}"
            )
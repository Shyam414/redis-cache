from cache.storage import CacheStorage
from protocol.parser import Parser
from commands.dispatcher import CommandDispatcher

storage = CacheStorage()

dispatcher = CommandDispatcher(storage)

while True:

    text = input(">> ")

    if text.lower() == "exit":
        break

    try:
        command = Parser.parse(text)

        response = dispatcher.dispatch(command)

        print(response)

    except Exception as e:
        print("Error:", e)
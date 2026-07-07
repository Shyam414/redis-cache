"""
PING command implementation.
"""


class PingCommand:
    """
    Executes the PING command.
    """

    @staticmethod
    def execute() -> str:
        """
        Returns a health check response.
        """

        return "PONG"
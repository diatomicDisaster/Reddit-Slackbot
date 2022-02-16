class ModFromSlackError(Exception):
    """Base class for modfromslack errors"""
    def __init__(self, message) -> None:
        super().__init__(message)

class MsgSendError(ModFromSlackError):
    """Failed to send Slack message"""
    def __init__(self, message) -> None:
        super().__init__(message)

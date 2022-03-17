from __future__ import (
    annotations,
)

class ModFromSlackError(Exception):
    """Base class for modfromslack errors"""
    def __init__(
        self, 
        message: str,
        *,
        preamble: str | None = None,
        afterword: str | None = None
    ) -> None:
        if preamble is not None:
            message = f"{preamble} {message}"
        if afterword is not None:
            message = f"{message}\n\n{afterword}"
        super().__init__(message)

class MsgSendError(ModFromSlackError):
    """Failed to send Slack message."""

class SequenceError(ModFromSlackError):
    """Something has happened in the wrong order."""
    def __init__(
        self, 
        should_be_first, 
        should_be_second,
        *,
        preamble: str | None = None,
        afterword: str | None = None
    ) -> None:
        message = f"Expected {should_be_first} before {should_be_second}"
        super().__init__(
            message,
            preamble = preamble,
            afterword = afterword
        )

class ActionSequenceError(SequenceError):
    """App thinks action came before its parent message."""
    def __init__(
        self, 
        parentmsg_ts, 
        action_ts,
        *,
        afterword=None
    ) -> None:
        _preamble=f"'message_ts' {parentmsg_ts} is later than 'action_ts' {action_ts}"
        super().__init__(
            "parent message", 
            "action",
            preamble=_preamble, 
            afterword=afterword
        )

class ConfigError(ModFromSlackError):
    """Error in config file format."""

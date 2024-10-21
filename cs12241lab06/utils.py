from typing import TypeGuard

from . import json_keys
from .project_types import JsonType, ChatMessageJson, MessageType, AuthenticatedMessageData


def is_chat_message(data: JsonType) -> TypeGuard[ChatMessageJson]:
    try:
        return isinstance(data, dict) and (
            data[json_keys.MSG_TYPE] == MessageType.CHAT and
            isinstance(data[json_keys.SRC], str) and
            isinstance(data[json_keys.DST], str) and
            isinstance(data[json_keys.MSG], str)
        )
    except KeyError:
        return False


def is_auth_success_message(data: JsonType) -> TypeGuard[AuthenticatedMessageData]:
    try:
        return isinstance(data, dict) and (
            data[json_keys.MSG_TYPE] == MessageType.AUTH_SUCCESS and
            isinstance(data[json_keys.CHATS], list)
        )
    except KeyError:
        return False


def make_error(msg_type: str | None):
    match msg_type:
        case MessageType.INCORRECT_FORMAT:
            return RuntimeError('Incorrect format')
        case MessageType.MISSING_JSON_KEYS:
            return RuntimeError('Missing JSON keys')
        case MessageType.INVALID_CREDENTIALS:
            return RuntimeError('Invalid credentials')
        case None:
            return RuntimeError(f"{json_keys.MSG_TYPE} key not found in JSON")
        case _:
            return RuntimeError(f"Unknown message type: {msg_type}")

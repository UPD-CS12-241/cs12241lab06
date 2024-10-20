from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any
from enum import StrEnum


JsonType = dict[str, Any] | list[Any] | str | int | float | bool | None


class MessageType(StrEnum):
    INCORRECT_FORMAT = 'INCORRECT_FORMAT'
    MISSING_JSON_KEYS = 'MISSING_JSON_KEYS'
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    AUTH_SUCCESS = 'AUTH_SUCCESS'
    CHAT = 'CHAT'


class AuthenticatedMessageJson(TypedDict):
    msg: str
    public_chats: list[str]


class AuthenticatedMessageData(TypedDict):
    msg: str
    chats: list[ChatMessageJson]


class ChatMessageJson(TypedDict):
    src: str
    dst: str | None
    msg: str


@dataclass
class ChatMessage:
    src: str
    dst: str | None
    msg: str

    @classmethod
    def from_json(cls, json: ChatMessageJson) -> ChatMessage:
        return ChatMessage(
            src=json['src'],
            dst=json['dst'],
            msg=json['msg'],
        )

    def to_json(self) -> ChatMessageJson:
        return {
            'src': self.src,
            'dst': self.dst,
            'msg': self.msg,
        }

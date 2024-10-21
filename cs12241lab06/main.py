import asyncio
from typing import Callable
import json

from websockets.client import connect, WebSocketClientProtocol

from . import json_keys
from .project_types import MessageType, ChatMessage, JsonType
from .utils import (
    is_chat_message,
    is_auth_success_message,
    make_error,
)


class Session:
    @classmethod
    async def start(cls, username: str, password: str, endpoint: str):
        """Attempt to start a session via the endpoint using the given credentials."""

        websocket = await connect(endpoint)
        await websocket.send(json.dumps({
            'username': username,
            'password': password,
        }))

        session = Session(username, endpoint, websocket)
        await session._fetch_chat_messages()

        return session

    def __init__(self, username: str, endpoint: str, websocket: WebSocketClientProtocol):
        self.username = username
        self.endpoint = endpoint
        self.chats: list[ChatMessage] = []
        self._websocket = websocket

    def send_group_message(self, msg: str):
        """Send a message to all users."""

        self._send_message(msg, None)

    def send_direct_message(self, msg: str, dest: str):
        """Send a message to a specific user."""

        self._send_message(msg, dest)

    def _send_message(self, msg: str, dest: str | None):
        async def task():
            await self._websocket.send(json.dumps({
                json_keys.MSG_TYPE: MessageType.CHAT,
                json_keys.SRC: self.username,
                json_keys.DST: dest,
                json_keys.MSG: msg,
            }))

        asyncio.create_task(task())

    async def _fetch_chat_messages(self):
        data = json.loads(await self._websocket.recv())

        if not is_auth_success_message(data):
            raise make_error(data.get(json_keys.MSG_TYPE))

        self.chats = [
            ChatMessage.from_json(chat_data)
            for chat_data in data[json_keys.CHATS]
        ]

    def make_task(self, on_chat_received: Callable[[ChatMessage], None]):
        """Create an awaitable for processing received messages via an event loop."""

        async def task_loop():
            while True:
                raw_data = str(await self._websocket.recv())
                print('Raw data:', raw_data)

                if is_chat_message(parsed_data := self._parse_message(raw_data)):
                    on_chat_received(ChatMessage.from_json(parsed_data))

        return task_loop

    def _parse_message(self, raw_data: str) -> JsonType:
        try:
            parsed_data = self._load_json(raw_data)
        except ValueError:
            raise make_error(MessageType.INCORRECT_FORMAT)

        if not isinstance(parsed_data, dict) or json_keys.MSG_TYPE not in parsed_data:
            raise make_error(MessageType.INCORRECT_FORMAT)

        return parsed_data

    def _load_json(self, raw_data: str) -> JsonType:
        # Needed to Pyright to upcast `dict[Unknown, Unknown]`
        return json.loads(raw_data)

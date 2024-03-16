"""Connection Manger Manages the websocket connections"""
from typing import List
from fastapi import WebSocket


class ConnectionManager:
    """Manages WS connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        """Accepts the websocket connection"""
        await ws.accept()
        self.active_connections.append(ws)

    async def send_pm(self, mess: str,  ws: WebSocket):
        """Sends Message `mess` to the websocket `ws`"""
        await ws.send_text(mess)

    def disconnect(self, ws: WebSocket):
        """Removes the websocket `ws` from active connections"""
        self.active_connections.remove(ws)

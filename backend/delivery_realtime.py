import asyncio
import json
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket

loop = None
connections: Dict[int, Set[WebSocket]] = defaultdict(set)


def init(event_loop):
    global loop
    loop = event_loop


async def connect(delivery_id: int, websocket: WebSocket):
    await websocket.accept()
    connections[delivery_id].add(websocket)


def disconnect(delivery_id: int, websocket: WebSocket):
    if websocket in connections.get(delivery_id, set()):
        connections[delivery_id].remove(websocket)
    if delivery_id in connections and not connections[delivery_id]:
        del connections[delivery_id]


async def _broadcast(delivery_id: int, payload: dict):
    dead = []
    message = json.dumps(payload, default=str)
    for websocket in list(connections.get(delivery_id, set())):
        try:
            await websocket.send_text(message)
        except Exception:
            dead.append(websocket)
    for websocket in dead:
        disconnect(delivery_id, websocket)


def notify_delivery(delivery_id: int, payload: dict):
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(_broadcast(delivery_id, payload), loop)

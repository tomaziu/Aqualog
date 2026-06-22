import asyncio
import json

_loop = None
connections = set()


def init(loop):
    global _loop
    _loop = loop


async def event_generator():
    queue = asyncio.Queue()
    connections.add(queue)
    try:
        yield f'data: {json.dumps({"type": "connected", "payload": {}}, ensure_ascii=False)}\n\n'
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=15)
                yield f'data: {data}\n\n'
            except asyncio.TimeoutError:
                yield 'event: ping\ndata: {}\n\n'
    except (asyncio.CancelledError, GeneratorExit):
        pass
    finally:
        connections.discard(queue)


async def _notify(event_type, payload):
    msg = json.dumps({'type': event_type, 'payload': payload or {}}, ensure_ascii=False)
    for q in list(connections):
        await q.put(msg)


def notify(event_type: str, payload: dict = None):
    if _loop is not None and _loop.is_running():
        asyncio.run_coroutine_threadsafe(_notify(event_type, payload), _loop)

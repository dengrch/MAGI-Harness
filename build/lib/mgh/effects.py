"""Explicit execution gate used by production and crash-prefix tests."""

import asyncio
import inspect
from collections import deque


class HarnessClosed(RuntimeError):
    pass


class HarnessFault(RuntimeError):
    pass


class Effects:
    def __init__(self, manual=False):
        self.manual = manual
        self.pending = deque()
        self.changed = asyncio.Event()
        self.closed = False
        self.driving = False

    async def call(self, kind, function, **details):
        if self.closed:
            raise HarnessClosed("Harness is closed")
        if self.manual:
            future = asyncio.get_running_loop().create_future()
            self.pending.append(({"kind": kind, **details}, future))
            self.changed.set()
            await future
        result = function()
        return await result if inspect.isawaitable(result) else result

    async def peek(self, task):
        if not self.manual:
            raise RuntimeError("Manual drive is disabled")
        while not self.pending and not task.done():
            self.changed.clear()
            if not self.pending and not task.done():
                await self.changed.wait()
        return self.pending[0][0] if self.pending else None

    async def execute(self, task):
        if self.driving:
            raise RuntimeError("Only one manual driver may execute a session")
        self.driving = True
        try:
            info = await self.peek(task)
            if info is None:
                return None
            _, future = self.pending.popleft()
            future.set_result(None)
            return await self.peek(task)
        finally:
            self.driving = False

    def close(self):
        self.closed = True
        while self.pending:
            _, future = self.pending.popleft()
            if not future.done():
                future.set_exception(HarnessClosed("Harness is closed"))
        self.changed.set()

"""Ordered interception and isolated observation for embedded applications."""

import inspect

from .store import canonical
import json


class Hooks:
    names = {"before_tool", "after_tool", "before_request", "after_response"}

    def __init__(self):
        self.handlers = {name: [] for name in self.names}

    def on(self, name, handler):
        if name not in self.handlers:
            raise ValueError("Unknown hook")
        self.handlers[name].append(handler)
        return lambda: self.handlers[name].remove(handler)

    async def run(self, name, value):
        current = json.loads(canonical(value))
        for handler in tuple(self.handlers[name]):
            patch = handler(json.loads(canonical(current)))
            if inspect.isawaitable(patch):
                patch = await patch
            if patch is not None:
                if not isinstance(patch, dict):
                    raise ValueError("Hook must return an object or None")
                current.update(json.loads(canonical(patch)))
        return current


class Watch:
    """A synchronous snapshot and subscription capture has no async gap."""

    def __init__(self, store, sid, snapshot):
        self.snapshot = snapshot
        self.buffer = []
        self.listener = None
        self.store = store
        self.sid = sid
        self.closed = False
        self.flushing = False
        store.observers.append(self.receive)

    def receive(self, sid, event):
        if self.closed or sid != self.sid:
            return
        if self.listener is None or self.flushing:
            self.buffer.append(event)
        else:
            self.deliver(event)

    def deliver(self, event):
        try:
            self.listener(json.loads(canonical(event)))
        except Exception:
            # Observers never participate in execution or durable decisions.
            return

    def start(self, listener):
        if self.closed or self.listener is not None:
            raise RuntimeError("Watch already started or closed")
        self.listener = listener
        self.flushing = True
        try:
            while self.buffer:
                self.deliver(self.buffer.pop(0))
        finally:
            self.flushing = False

    def unsubscribe(self):
        if not self.closed:
            self.closed = True
            self.store.observers.remove(self.receive)
            self.buffer.clear()

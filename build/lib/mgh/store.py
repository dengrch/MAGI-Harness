"""One SQLite journal and content-addressed source store. No model dependencies."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import deque
from contextlib import contextmanager
from pathlib import Path
from time import time
from uuid import uuid4


def canonical(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Store:
    """Immutable sources and ordered events, scoped by workspace AND session.

    A process lock prevents competing runtime writers. SQLite transactions commit
    each event with its source. Opening a store does not recover running sessions;
    recovery belongs to the single server owner after acquiring its process lock.
    """

    def __init__(self, path: str | Path, workspace: str = "default"):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.workspace = workspace
        self.observers = []
        self._notifications = deque()
        self._notifying = False
        self.db = sqlite3.connect(self.path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                workspace TEXT, id TEXT, title TEXT, config TEXT, created REAL,
                PRIMARY KEY (workspace,id));
            CREATE TABLE IF NOT EXISTS sources (
                workspace TEXT, session TEXT, ref TEXT, body TEXT, hash TEXT,
                PRIMARY KEY (workspace,session,ref));
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace TEXT, session TEXT, kind TEXT, turn TEXT,
                ref TEXT, created REAL);
            CREATE INDEX IF NOT EXISTS events_session ON events(workspace,session,seq);
            CREATE TABLE IF NOT EXISTS operations (
                workspace TEXT, session TEXT, id TEXT, start_seq INTEGER,
                PRIMARY KEY (workspace,session));
            CREATE INDEX IF NOT EXISTS events_turn ON events(workspace,session,turn,seq);
        """)

    @contextmanager
    def writer(self):
        # Local application: one serving process, any number of async sessions.
        import fcntl

        with open(str(self.path) + ".lock", "a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError(
                    "Another Harness process owns this database"
                ) from exc
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def create(self, config: dict, title: str = "新对话") -> str:
        sid = uuid4().hex
        self.db.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?)",
            (self.workspace, sid, title, canonical(config), time()),
        )
        return sid

    def session(self, sid: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM sessions WHERE workspace=? AND id=?", (self.workspace, sid)
        ).fetchone()
        if row is None:
            raise KeyError(sid)
        return {**dict(row), "config": json.loads(row["config"])}

    def sessions(self) -> list[dict]:
        return [
            self.session(row[0])
            for row in self.db.execute(
                "SELECT id FROM sessions WHERE workspace=? ORDER BY created DESC",
                (self.workspace,),
            )
        ]

    def rename(self, sid: str, title: str):
        self.session(sid)
        self.db.execute(
            "UPDATE sessions SET title=? WHERE workspace=? AND id=?",
            (title[:80], self.workspace, sid),
        )

    def update_config(self, sid: str, **changes) -> dict:
        session = self.session(sid)
        config = {**session["config"], **changes}
        self.db.execute(
            "UPDATE sessions SET config=? WHERE workspace=? AND id=?",
            (canonical(config), self.workspace, sid),
        )
        return self.session(sid)

    def put(self, sid: str, value) -> str:
        self.session(sid)
        body, sha = canonical(value), digest(value)
        scope = hashlib.sha256(f"{self.workspace}\0{sid}".encode()).hexdigest()[:24]
        ref = f"ctx://v1/{scope}/{sha}"
        self.db.execute(
            "INSERT OR IGNORE INTO sources VALUES (?,?,?,?,?)",
            (self.workspace, sid, ref, body, sha),
        )
        return ref

    def get(self, sid: str, ref: str):
        row = self.db.execute(
            "SELECT body,hash FROM sources WHERE workspace=? AND session=? AND ref=?",
            (self.workspace, sid, ref),
        ).fetchone()
        if row is None:
            raise KeyError(f"Missing or foreign source: {ref}")
        value = json.loads(row[0])
        if digest(value) != row[1] or not ref.endswith("/" + row[1]):
            raise ValueError(f"Source integrity failure: {ref}")
        return value

    def get_many(self, sid: str, refs: list[str]) -> list:
        return [self.get(sid, ref) for ref in refs]

    def append(self, sid: str, kind: str, value: dict, turn: str | None = None) -> dict:
        return self.append_batch(sid, [(kind, value)], turn)[0]

    def append_batch(
        self, sid: str, items: list[tuple[str, dict]], turn: str | None = None
    ) -> list[dict]:
        """Commit related events and their sources together, or none of them."""
        result = []
        self.db.execute("BEGIN IMMEDIATE")
        try:
            for kind, value in items:
                ref = self.put(sid, value)
                created = time()
                cur = self.db.execute(
                    "INSERT INTO events(workspace,session,kind,turn,ref,created) VALUES (?,?,?,?,?,?)",
                    (self.workspace, sid, kind, turn, ref, created),
                )
                result.append(
                    dict(
                        seq=cur.lastrowid,
                        kind=kind,
                        turn=turn,
                        ref=ref,
                        created=created,
                        data=value,
                    )
                )
                if kind == "operation_started":
                    self.db.execute(
                        "INSERT INTO operations VALUES (?,?,?,?)",
                        (self.workspace, sid, turn, cur.lastrowid),
                    )
                elif kind == "operation_finished":
                    changed = self.db.execute(
                        "DELETE FROM operations WHERE workspace=? AND session=? AND id=?",
                        (self.workspace, sid, turn),
                    ).rowcount
                    if changed != 1:
                        raise ValueError("Finishing an operation that is not open")
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        self._notifications.extend((sid, event) for event in result)
        if not self._notifying:
            self._notifying = True
            try:
                while self._notifications:
                    session, event = self._notifications.popleft()
                    for observer in tuple(self.observers):
                        try:
                            observer(session, json.loads(canonical(event)))
                        except Exception:
                            continue
            finally:
                self._notifying = False
        return result

    def open_operation(self, sid: str) -> dict | None:
        row = self.db.execute(
            "SELECT start_seq FROM operations WHERE workspace=? AND session=?",
            (self.workspace, sid),
        ).fetchone()
        if row is None:
            return None
        event = self.db.execute(
            "SELECT seq,kind,turn,ref,created FROM events WHERE seq=? AND workspace=? AND session=?",
            (row[0], self.workspace, sid),
        ).fetchone()
        if event is None or event["kind"] != "operation_started":
            raise ValueError("Corrupt open-operation projection")
        return {**dict(event), "data": self.get(sid, event["ref"])}

    def legacy_unclosed_turns(self, sid):
        return [
            row[0]
            for row in self.db.execute(
                "SELECT e.turn FROM events e WHERE e.workspace=? AND e.session=? AND e.kind='turn_start' "
                "AND NOT EXISTS (SELECT 1 FROM events x WHERE x.workspace=e.workspace AND x.session=e.session "
                "AND x.turn=e.turn AND x.kind IN ('turn_end','operation_started'))",
                (self.workspace, sid),
            )
        ]

    def operation_events(self, sid: str, turn: str) -> list[dict]:
        return [
            {**dict(row), "data": self.get(sid, row["ref"])}
            for row in self.db.execute(
                "SELECT seq,kind,turn,ref,created FROM events "
                "WHERE workspace=? AND session=? AND turn=? ORDER BY seq",
                (self.workspace, sid, turn),
            )
        ]

    def events(self, sid: str, after: int = 0) -> list[dict]:
        self.session(sid)
        return [
            {**dict(row), "data": self.get(sid, row["ref"])}
            for row in self.db.execute(
                "SELECT seq,kind,turn,ref,created FROM events WHERE workspace=? AND session=? AND seq>? ORDER BY seq",
                (self.workspace, sid, after),
            )
        ]

    def close(self):
        self.db.close()

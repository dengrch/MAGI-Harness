"""Pure validation of an operation's committed journal prefix."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationState:
    operation_id: str
    aborting: bool
    attempts: int
    finished: bool
    pending_tools: tuple[str, ...]


def reduce_operation(events: list[dict]) -> OperationState:
    starts = [e for e in events if e["kind"] == "operation_started"]
    if len(starts) != 1:
        raise ValueError("Operation must have exactly one start")
    turn = starts[0]["turn"]
    attempts = 0
    finished = aborting = False
    intents = set()
    calls = {}
    results = set()
    previous = 0
    for event in events:
        if event["seq"] <= previous or event["turn"] != turn:
            raise ValueError("Invalid operation order or identity")
        previous = event["seq"]
        kind, data = event["kind"], event["data"]
        if finished:
            raise ValueError("Record after operation finish")
        if kind == "abort_requested":
            aborting = True
        elif kind == "queue_enqueued" and aborting:
            raise ValueError("Conversational queue accepted after abort")
        elif kind == "step_attempt":
            attempts += 1
            if data["attempt"] != attempts:
                raise ValueError("Non-consecutive attempt number")
        elif kind == "response":
            attempts = 0
        elif kind == "message":
            for index, call in enumerate(data.get("tool_calls", [])):
                calls[(event["seq"], index)] = call
            if data.get("tool_call_id"):
                results.add(data["tool_call_id"])
        elif kind == "tool_intent":
            key = (data["assistant_seq"], data["index"])
            if key in intents:
                raise ValueError("Duplicate tool invocation intent")
            call = calls.get(key)
            if (
                call is None
                or call["id"] != data["id"]
                or call["function"]["name"] != data["name"]
            ):
                raise ValueError("Tool intent does not match assistant call")
            intents.add(key)
        elif kind == "operation_finished":
            finished = True
    return OperationState(
        turn,
        aborting,
        attempts,
        finished,
        tuple(c["id"] for c in calls.values() if c["id"] not in results),
    )

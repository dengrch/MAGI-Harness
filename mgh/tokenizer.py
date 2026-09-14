"""Explicit tokenizer selection; serialized input tokens are not server cache keys."""

from functools import lru_cache


@lru_cache(maxsize=8)
def encoding(name):
    try:
        import tiktoken
    except ImportError as exc:
        raise ValueError(
            "Install magi-harness[tokenizer] to select a tokenizer"
        ) from exc
    return tiktoken.get_encoding(name)


def tokens(text: str, name: str) -> list[int]:
    return encoding(name).encode(text, disallowed_special=())


def common_prefix(left, right):
    count = 0
    for a, b in zip(left, right):
        if a != b:
            break
        count += 1
    return count

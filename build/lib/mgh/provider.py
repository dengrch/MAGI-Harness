"""Two providers with the same streaming boundary; no SDK or adapter registry."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from uuid import uuid4

import httpx


class ProviderError(RuntimeError):
    def __init__(self, message, *, retryable=False, overflow=False):
        super().__init__(message)
        self.retryable = retryable
        self.overflow = overflow


def _provider_failure(response: httpx.Response) -> ProviderError:
    detail = ""
    try:
        body = response.json()
        error = body.get("error", body) if isinstance(body, dict) else {}
        if isinstance(error, dict):
            detail = str(error.get("message") or error.get("code") or "")
    except (ValueError, AttributeError):
        pass
    # Preserve a bounded provider-authored diagnosis but never echo secrets.
    detail = detail.replace(response.request.headers.get("authorization", ""), "")
    detail = " ".join(detail.split())[:300]
    suffix = f": {detail}" if detail else ""
    return ProviderError(
        f"Provider HTTP {response.status_code}{suffix}",
        retryable=response.status_code in {408, 429, 500, 502, 503, 504},
        overflow=any(
            term in detail.lower()
            for term in (
                "context_length_exceeded",
                "maximum context length",
                "context window",
            )
        ),
    )


@dataclass
class CompatibleProvider:
    model: str
    base_url: str
    api_key: str
    timeout: float = 120
    binding: str = "openai"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def prepare_payload(self, payload: dict) -> dict:
        """Return the exact wire payload without mutating the context snapshot."""
        if self.binding == "llamacpp":
            return {**payload, "cache_prompt": True}
        return payload

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.base_url.rstrip("/") + "/models", headers=self._headers()
            )
        if response.is_error:
            raise _provider_failure(response)
        try:
            data = response.json().get("data", [])
            return sorted(
                item["id"] for item in data if isinstance(item, dict) and item.get("id")
            )
        except (AttributeError, TypeError, ValueError) as exc:
            raise ProviderError("Provider returned an invalid model list") from exc

    async def stream(self, payload: dict):
        payload = self.prepare_payload(payload)
        message = dict(role="assistant", content="")
        calls, usage, finish = {}, None, None
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.base_url.rstrip("/") + "/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                if response.is_error:
                    raise _provider_failure(response)
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    chunk = json.loads(data)
                    if chunk.get("error"):
                        raise ProviderError("Provider reported a stream error")
                    if chunk.get("usage") is not None:
                        usage = chunk["usage"]
                    for choice in chunk.get("choices", []):
                        if choice.get("index", 0) != 0:
                            continue
                        finish = choice.get("finish_reason") or finish
                        delta = choice.get("delta", {})
                        for key in ("content", "reasoning_content"):
                            value = delta.get(key)
                            if key == "reasoning_content" and not value:
                                value = delta.get("reasoning")
                            if value:
                                message[key] = message.get(key, "") + value
                                yield dict(kind="delta", field=key, text=value)
                        for call in delta.get("tool_calls", []):
                            c = calls.setdefault(
                                call["index"],
                                dict(
                                    id="",
                                    type="function",
                                    function=dict(name="", arguments=""),
                                ),
                            )
                            if call.get("id"):
                                c["id"] = call["id"]
                            for key in ("name", "arguments"):
                                c["function"][key] += call.get("function", {}).get(
                                    key, ""
                                )
        if finish is None:
            raise ProviderError("Provider stream ended without a finish reason")
        if calls:
            message["tool_calls"] = [calls[k] for k in sorted(calls)]
            if any(not c["id"] or not c["function"]["name"] for c in calls.values()):
                raise ProviderError("Incomplete tool call")
        yield dict(
            kind="completion", message=message, usage=usage, finish_reason=finish
        )


class FakeProvider:
    """Offline demo, explicitly not an LLM or a source of token usage."""

    model = "offline-demo"

    async def stream(self, payload: dict):
        last = payload["messages"][-1]
        text = last.get("content", "")
        message = dict(role="assistant", content="")
        if last["role"] == "user" and text.startswith(("/calc ", "/read ")):
            read = text.startswith("/read ")
            name, key = ("context_read", "ref") if read else ("calculate", "expression")
            message["tool_calls"] = [
                dict(
                    id="call_" + uuid4().hex,
                    type="function",
                    function=dict(
                        name=name, arguments=json.dumps({key: text.split(" ", 1)[1]})
                    ),
                )
            ]
        else:
            if last["role"] == "tool":
                reply = "工具返回：\n" + text
            else:
                reply = (
                    "已记录这轮对话。当前为离线演示模式，可输入 /calc (12 + 8) * 3 体验工具调用；连续对话后，在 Trace 中查看 Hot → Cold → Stubs 的变化。\n\n你刚才说："
                    + text
                )
            for i in range(0, len(reply), 12):
                await asyncio.sleep(0.015)
                yield dict(kind="delta", field="content", text=reply[i : i + 12])
            message["content"] = reply
        yield dict(
            kind="completion",
            message=message,
            usage=None,
            finish_reason="tool_calls" if message.get("tool_calls") else "stop",
        )


def usage_metrics(usage: dict | None) -> dict:
    raw = usage or {}
    details = raw.get("prompt_tokens_details") or {}
    return dict(
        input_tokens=raw.get("prompt_tokens"),
        output_tokens=raw.get("completion_tokens"),
        cache_read_tokens=details.get(
            "cached_tokens", raw.get("prompt_cache_hit_tokens")
        ),
        cache_write_tokens=raw.get("cache_creation_input_tokens"),
        raw=usage,
    )

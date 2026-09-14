"""Run with python -m mgh; demo is offline by default."""

import argparse
import asyncio
import os

from .context import ContextConfig
from .runtime import Harness
from .settings import (
    PreferencesStore,
    ProviderSettings,
    SettingsStore,
    default_data_dir,
)
from .store import Store


def main():
    parser = argparse.ArgumentParser(description="MAGI Harness: Python context runtime")
    parser.add_argument("--data-dir", default=str(default_data_dir()))
    parser.add_argument("--db")
    parser.add_argument("--workspace", default="default")
    parser.add_argument("--port", type=int, default=34914)
    parser.add_argument(
        "--provider",
        choices=["auto", "demo", "openai", "ollama", "llamacpp", "compatible"],
        default="auto",
    )
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--session")
    parser.add_argument(
        "--policy",
        choices=[
            "four_zone",
            "full_history",
            "sliding_window",
            "traditional_compaction",
        ],
        default="four_zone",
    )
    args = parser.parse_args()
    data_dir = os.path.abspath(os.path.expanduser(args.data_dir))
    settings_store = SettingsStore(os.path.join(data_dir, "settings.json"))
    preferences_store = PreferencesStore(os.path.join(data_dir, "preferences.json"))
    settings = settings_store.load()
    if args.provider != "auto":
        binding = "openai" if args.provider == "compatible" else args.provider
        settings = ProviderSettings(
            binding=binding,
            model=os.environ.get("LLM_MODEL")
            or os.environ.get("HARNESS_MODEL")
            or ("offline-demo" if binding == "demo" else settings.model),
            host=os.environ.get("LLM_BINDING_HOST")
            or os.environ.get("HARNESS_BASE_URL")
            or settings.host,
            api_key=os.environ.get("LLM_BINDING_API_KEY")
            or os.environ.get("HARNESS_API_KEY")
            or settings.api_key,
            timeout=settings.timeout,
        ).validated()
    provider = settings.provider()
    store = Store(args.db or os.path.join(data_dir, "context.db"), args.workspace)
    harness = Harness(store, provider)
    if args.cli:

        async def chat():
            with store.writer():
                harness.recover()
                sid = args.session or harness.create(ContextConfig(policy=args.policy))
                print(f"MAGI Harness · {provider.model} · session {sid}")
                while True:
                    try:
                        text = await asyncio.to_thread(input, "you> ")
                    except (EOFError, KeyboardInterrupt):
                        break
                    if text == "/quit":
                        break
                    if text == "/resume":
                        result = await harness.resume(sid)
                        print(result)
                        continue
                    if text == "/abort":
                        await harness.cancel(sid)
                        continue
                    if text == "/compact":
                        print(await harness.compact(sid))
                        continue
                    if not text.strip():
                        continue
                    result = await harness.run(sid, text)
                    print(
                        result.get("content", "")
                        if result
                        else "Run stopped. See persisted trace."
                    )

        try:
            asyncio.run(chat())
        finally:
            store.close()
    else:
        import uvicorn
        from .web import create_app

        uvicorn.run(
            create_app(harness, settings_store, preferences_store),
            host="127.0.0.1",
            port=args.port,
        )
        store.close()


if __name__ == "__main__":
    main()

"""Direct MAGI Memo integration; no runtime REST or implicit memory writes."""

from .store import Store
from .tools import Tool, string_parameter


def workspace_store(workspace_root, workspace_id="default"):
    """Keep exact context separate from ragstore and Episode/Atom extraction.

    Provisional local layout; this does not initialize or claim ownership of a
    MagiRuntime instance. The embedding application owns workspace lifecycle.
    """
    from pathlib import Path

    return Store(Path(workspace_root) / "contexts" / "harness.db", workspace_id)


def memo_tools(handle):
    """Use an already-open MagiHandle. Its public API enforces lifecycle leases."""

    async def search(args):
        return await handle.search(args["query"], only_need_context=True)

    return [
        Tool(
            "memory_search",
            "Search MAGI Memo for relevant long-term memory. Reading does not write memory.",
            string_parameter("query"),
            search,
        )
    ]

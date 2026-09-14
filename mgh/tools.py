"""Workspace-scoped baseline tools inspired by DSH's core bundle."""

from __future__ import annotations

import ast
import fnmatch
import operator
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable


@dataclass
class ToolContext:
    workspace: Path
    reads: set[Path] = field(default_factory=set)

    def resolve(self, value: str = ".", *, directory: bool | None = None) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Path must be a non-empty string")
        root = self.workspace.resolve()
        raw = Path(value).expanduser()
        target = (raw if raw.is_absolute() else root / raw).resolve()
        if not target.is_relative_to(root):
            raise PermissionError("Path is outside the session workspace")
        if directory is True and (not target.exists() or not target.is_dir()):
            raise FileNotFoundError("Directory does not exist")
        if directory is False and (not target.exists() or not target.is_file()):
            raise FileNotFoundError("File does not exist")
        return target

    def display(self, target: Path) -> str:
        relative = target.resolve().relative_to(self.workspace.resolve())
        return "." if not relative.parts else relative.as_posix()


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    run: Callable[..., Awaitable[object]]
    risk: str = "read"
    workspace_aware: bool = False
    replay: str = "never"
    parallel: bool = False

    def __post_init__(self):
        if self.replay not in {"never", "safe"}:
            raise ValueError("Tool replay must be never or safe")

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def object_parameters(properties: dict, required: list[str] = ()):
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def string_parameter(name: str):
    return object_parameters({name: {"type": "string"}}, [name])


async def calculate(args):
    expression = args["expression"]
    if not isinstance(expression, str) or len(expression) > 200:
        raise ValueError("Expression must be at most 200 characters")
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (float, int):
            result = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in ops:
            result = ops[type(node.op)](evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            result = ops[type(node.op)](evaluate(node.operand))
        else:
            raise ValueError("Only numbers and + - * / are supported")
        if abs(result) > 1e100:
            raise ValueError("Result too large")
        return result

    return {"result": evaluate(ast.parse(expression, mode="eval").body)}


async def read_file(args, ctx: ToolContext):
    target = ctx.resolve(args["file_path"], directory=False)
    offset = int(args.get("offset", 1))
    limit = int(args.get("limit", 500))
    if offset < 1 or limit < 1 or limit > 2000:
        raise ValueError("offset must be positive and limit must be 1..2000")
    lines = target.read_text(encoding="utf-8").splitlines()
    selected = lines[offset - 1 : offset - 1 + limit]
    ctx.reads.add(target)
    return {
        "path": ctx.display(target),
        "content": "\n".join(
            f"{n:>6}\t{line}" for n, line in enumerate(selected, offset)
        ),
        "lines": len(selected),
        "total_lines": len(lines),
        "truncated": offset - 1 + len(selected) < len(lines),
    }


def _files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not any(
            part in {".git", "node_modules", ".venv"} for part in path.parts
        ):
            yield path


async def glob_files(args, ctx: ToolContext):
    root = ctx.resolve(args.get("path", "."), directory=True)
    pattern = args["pattern"]
    matches = [
        ctx.display(path)
        for path in _files(root)
        if fnmatch.fnmatch(path.relative_to(root).as_posix(), pattern)
    ]
    matches.sort()
    return {
        "matches": matches[:500],
        "count": len(matches),
        "truncated": len(matches) > 500,
    }


async def grep_files(args, ctx: ToolContext):
    root = ctx.resolve(args.get("path", "."))
    regex = re.compile(args["pattern"])
    include = args.get("include")
    paths = [root] if root.is_file() else list(_files(root))
    matches = []
    for path in paths:
        relative = ctx.display(path)
        if include and not fnmatch.fnmatch(relative, include):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            if regex.search(line):
                matches.append({"path": relative, "line": number, "text": line[:1000]})
                if len(matches) >= 500:
                    return {"matches": matches, "truncated": True}
    return {"matches": matches, "truncated": False}


async def write_file(args, ctx: ToolContext):
    target = ctx.resolve(args["file_path"])
    if target.exists() and target not in ctx.reads:
        raise PermissionError("Read the existing file before replacing it")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(args["content"], encoding="utf-8")
    ctx.reads.add(target)
    return {"path": ctx.display(target), "bytes": len(args["content"].encode())}


async def edit_file(args, ctx: ToolContext):
    target = ctx.resolve(args["file_path"], directory=False)
    if target not in ctx.reads:
        raise PermissionError("Read the file before editing it")
    old, new = args["old_string"], args["new_string"]
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        raise ValueError("old_string was not found")
    replace_all = bool(args.get("replace_all", False))
    if not replace_all and count != 1:
        raise ValueError("old_string must be unique unless replace_all is true")
    target.write_text(
        text.replace(old, new, -1 if replace_all else 1), encoding="utf-8"
    )
    return {"path": ctx.display(target), "replacements": count if replace_all else 1}


async def bash(args, ctx: ToolContext):
    import asyncio

    workdir = ctx.resolve(args.get("workdir", "."), directory=True)
    timeout = min(max(float(args.get("timeout_seconds", 30)), 1), 120)
    process = await asyncio.create_subprocess_exec(
        "/bin/bash",
        "-lc",
        args["command"],
        cwd=workdir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except TimeoutError:
        process.kill()
        await process.wait()
        raise TimeoutError("Command timed out") from None
    cap = 100_000
    return {
        "exit_code": process.returncode,
        "stdout": stdout[:cap].decode(errors="replace"),
        "stderr": stderr[:cap].decode(errors="replace"),
        "truncated": len(stdout) > cap or len(stderr) > cap,
        "workdir": ctx.display(workdir),
    }


def basic_tools():
    path = {"type": "string", "description": "Path inside the session workspace."}
    return [
        Tool(
            "calculate",
            "Evaluate numeric arithmetic (+ - * / and parentheses).",
            string_parameter("expression"),
            calculate,
        ),
        Tool(
            "read",
            "Read a UTF-8 text file and return line-numbered content.",
            object_parameters(
                {
                    "file_path": path,
                    "offset": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
                ["file_path"],
            ),
            read_file,
            workspace_aware=True,
        ),
        Tool(
            "glob",
            "Find files whose paths match a glob pattern.",
            object_parameters(
                {"pattern": {"type": "string"}, "path": path}, ["pattern"]
            ),
            glob_files,
            workspace_aware=True,
        ),
        Tool(
            "grep",
            "Search UTF-8 file contents with a regular expression.",
            object_parameters(
                {
                    "pattern": {"type": "string"},
                    "path": path,
                    "include": {"type": "string"},
                },
                ["pattern"],
            ),
            grep_files,
            workspace_aware=True,
        ),
        Tool(
            "write",
            "Create or fully replace a UTF-8 text file.",
            object_parameters(
                {"file_path": path, "content": {"type": "string"}},
                ["file_path", "content"],
            ),
            write_file,
            risk="write",
            workspace_aware=True,
        ),
        Tool(
            "edit",
            "Edit an existing UTF-8 text file by replacing literal text.",
            object_parameters(
                {
                    "file_path": path,
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                    "replace_all": {"type": "boolean"},
                },
                ["file_path", "old_string", "new_string"],
            ),
            edit_file,
            risk="write",
            workspace_aware=True,
        ),
        Tool(
            "bash",
            "Run a bash command in the session workspace. Always requires user approval.",
            object_parameters(
                {
                    "command": {"type": "string"},
                    "description": {"type": "string"},
                    "workdir": path,
                    "timeout_seconds": {"type": "number"},
                },
                ["command", "description"],
            ),
            bash,
            risk="execute",
            workspace_aware=True,
        ),
    ]

"""Utility helpers shared across the application."""
from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

import pathspec
import tiktoken

__all__ = [
    "count_tokens",
    "sanitize_tag",
    "is_binary",
    "render_tree_structure",
    "build_gitignore_spec",
]

def count_tokens(text: str) -> int:
    """Return the number of tokens for *text* using tiktoken's cl100k_base encoding."""
    encoder = tiktoken.get_encoding("cl100k_base")
    return len(encoder.encode(text))

def sanitize_tag(name: str) -> str:
    """Return *name* where every non-alphanumeric character is replaced with “_”."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

def is_binary(path: str) -> bool:
    """Heuristic check whether *path* is a binary file (cannot be opened as UTF-8)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1024)
        return False
    except UnicodeDecodeError:
        return True

def render_tree_structure(rel_paths: List[str]) -> str:
    """Return an ASCII tree representation for *rel_paths* (list of paths relative to root)."""
    root: Dict[str, Dict | None] = {}
    for p in rel_paths:
        parts = p.split("/")
        cur = root
        for idx, part in enumerate(parts):
            if idx == len(parts) - 1:
                cur[part] = None
            else:
                cur = cur.setdefault(part, {})

    lines: List[str] = ["."]

    def walk(subtree: Dict[str, Dict | None], prefix: str = "") -> None:
        dirs = sorted(k for k, v in subtree.items() if isinstance(v, dict))
        files = sorted(k for k, v in subtree.items() if v is None)
        for i, name in enumerate([*dirs, *files]):
            is_last = i == (len(dirs) + len(files) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if isinstance(subtree[name], dict):
                extension = "    " if is_last else "│   "
                walk(subtree[name], prefix + extension)

    walk(root)
    return "\n".join(lines)

def build_gitignore_spec(root_dir: str):
    """Return a PathSpec built from all .gitignore files under *root_dir* (or None)."""
    patterns: List[str] = []
    for current_root, _dirs, files in os.walk(root_dir):
        if ".gitignore" in files:
            gi_path = os.path.join(current_root, ".gitignore")
            try:
                with open(gi_path, encoding="utf-8") as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or line.startswith("#"):
                            continue
                        rel_base = os.path.relpath(current_root, root_dir).replace(os.sep, "/")
                        if rel_base != ".":
                            line = f"{rel_base}/{line}"
                        patterns.append(line)
            except OSError:
                pass
    if patterns:
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return None
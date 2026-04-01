"""Modele domenowe dla sesji budowania promptu."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class EntrySourceType(StrEnum):
    """Typ źródła wpisu w sesji."""

    FILE = "file"
    DIRECTORY_FILE = "directory_file"
    DIRECTORY_TREE = "directory_tree"


class OutputFormat(StrEnum):
    """Wspierane profile wyjścia renderera."""

    XML = "xml"
    MARKDOWN = "markdown"
    PLAIN = "plain"


@dataclass(slots=True)
class Entry:
    """Pojedynczy element wejścia sesji."""

    entry_id: str
    path: str
    source_type: EntrySourceType
    content: str
    include_in_output: bool = True
    read_error: str | None = None
    is_binary: bool = False
    size: int = 0
    token_count_cache: int | None = None
    last_loaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Session:
    """Stan sesji jako źródło prawdy dla renderowania outputu."""

    prompt_text: str = ""
    entries: list[Entry] = field(default_factory=list)
    output_format: OutputFormat = OutputFormat.XML


@dataclass(slots=True)
class BuildResult:
    """Wynik renderowania outputu ze stanu sesji."""

    rendered_output: str
    total_tokens: int
    included_entries: int
    excluded_entries: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

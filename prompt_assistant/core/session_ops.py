"""Operacje na stanie sesji."""
from __future__ import annotations

from uuid import uuid4

from .models import Entry, EntrySourceType, Session


def create_entry(
    path: str,
    source_type: EntrySourceType,
    content: str,
    *,
    include_in_output: bool = True,
    read_error: str | None = None,
    is_binary: bool = False,
    size: int = 0,
) -> Entry:
    """Tworzy wpis sesji z unikalnym identyfikatorem."""
    return Entry(
        entry_id=str(uuid4()),
        path=path,
        source_type=source_type,
        content=content,
        include_in_output=include_in_output,
        read_error=read_error,
        is_binary=is_binary,
        size=size,
    )


def add_entry(session: Session, entry: Entry) -> None:
    """Dodaje wpis do sesji."""
    session.entries.append(entry)


def remove_entry(session: Session, entry_id: str) -> bool:
    """Usuwa wpis po identyfikatorze; zwraca True gdy usunięto."""
    for index, entry in enumerate(session.entries):
        if entry.entry_id == entry_id:
            del session.entries[index]
            return True
    return False


def set_entry_inclusion(session: Session, entry_id: str, include: bool) -> bool:
    """Ustawia flagę include_in_output wpisu."""
    entry = get_entry(session, entry_id)
    if entry is None:
        return False
    entry.include_in_output = include
    return True


def get_entry(session: Session, entry_id: str) -> Entry | None:
    """Zwraca wpis po ID albo None."""
    for entry in session.entries:
        if entry.entry_id == entry_id:
            return entry
    return None


def clear_session(session: Session) -> None:
    """Czyści prompt i wszystkie wpisy sesji."""
    session.prompt_text = ""
    session.entries.clear()

"""Masowe operacje na wpisach sesji."""
from __future__ import annotations

from .models import Session
from .session_ops import remove_entry, set_entry_inclusion


def include_entries(session: Session, entry_ids: list[str]) -> int:
    """Włącza wskazane wpisy do outputu; zwraca liczbę zmian."""
    changed = 0
    for entry_id in entry_ids:
        if set_entry_inclusion(session, entry_id, True):
            changed += 1
    return changed


def exclude_entries(session: Session, entry_ids: list[str]) -> int:
    """Wyłącza wskazane wpisy z outputu; zwraca liczbę zmian."""
    changed = 0
    for entry_id in entry_ids:
        if set_entry_inclusion(session, entry_id, False):
            changed += 1
    return changed


def remove_entries(session: Session, entry_ids: list[str]) -> int:
    """Usuwa wskazane wpisy; zwraca liczbę usunięć."""
    removed = 0
    for entry_id in entry_ids:
        if remove_entry(session, entry_id):
            removed += 1
    return removed

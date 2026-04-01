"""Liczenie tokenów dla sesji i wpisów."""
from __future__ import annotations

from prompt_assistant.utils import count_tokens

from .models import Entry, Session


def count_entry_tokens(entry: Entry) -> int:
    """Zwraca liczbę tokenów wpisu z prostym cache."""
    if entry.token_count_cache is None:
        entry.token_count_cache = count_tokens(entry.content)
    return entry.token_count_cache


def count_session_tokens(session: Session) -> tuple[int, int, int]:
    """Zwraca tokeny: (prompt, attachments, suma)."""
    prompt_tokens = count_tokens(session.prompt_text) if session.prompt_text else 0

    attachment_tokens = 0
    for entry in session.entries:
        if entry.include_in_output and entry.read_error is None:
            attachment_tokens += count_entry_tokens(entry)

    return prompt_tokens, attachment_tokens, prompt_tokens + attachment_tokens

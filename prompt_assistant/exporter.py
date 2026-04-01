"""Funkcje eksportu finalnego outputu."""
from __future__ import annotations


def export_text_to_file(path: str, content: str) -> None:
    """Zapisuje wynik do pliku UTF-8."""
    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(content)

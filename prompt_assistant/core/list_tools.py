"""Narzędzia filtrowania listy i raportowania importu."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FileListRecord:
    """Dane używane do filtrowania pozycji listy plików."""

    display_name: str
    extension: str
    status: str


def matches_filters(
    record: FileListRecord,
    *,
    name_query: str,
    extension_query: str,
    status_filter: str,
) -> bool:
    """Sprawdza, czy rekord spełnia filtry nazwy/rozszerzenia/statusu."""
    normalized_name = name_query.strip().lower()
    normalized_ext = extension_query.strip().lower()
    normalized_status = status_filter.strip().lower()

    if normalized_name and normalized_name not in record.display_name.lower():
        return False

    if normalized_ext:
        candidate = normalized_ext if normalized_ext.startswith(".") else f".{normalized_ext}"
        if record.extension.lower() != candidate:
            return False

    if normalized_status and normalized_status != "all":
        if record.status.lower() != normalized_status:
            return False

    return True


def build_import_report(
    *,
    added_count: int,
    skipped_git: int,
    skipped_custom: int,
    skipped_binary: int,
    read_errors: list[str],
) -> str:
    """Buduje czytelny raport po imporcie katalogu."""
    lines = [
        f"Dodano: {added_count}",
        f"Pominięto .gitignore: {skipped_git}",
        f"Pominięto custom: {skipped_custom}",
        f"Pominięto binarne: {skipped_binary}",
        f"Błędy odczytu: {len(read_errors)}",
    ]

    if read_errors:
        lines.append("")
        lines.append("Szczegóły błędów odczytu:")
        lines.extend(read_errors[:10])
        if len(read_errors) > 10:
            lines.append(f"... (+{len(read_errors) - 10} kolejnych)")

    return "\n".join(lines)

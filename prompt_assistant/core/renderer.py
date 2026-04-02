"""Renderer finalnego outputu promptu ze stanu sesji."""
from __future__ import annotations

from .models import BuildResult, Entry, EntrySourceType, OutputFormat, Session
from .token_service import count_session_tokens


def _render_xml_entry(entry: Entry, lines: list[str]) -> None:
    if entry.source_type == EntrySourceType.DIRECTORY_TREE:
        lines.append("<directories>")
        lines.extend(entry.content.splitlines())
        lines.append("</directories>")
        return

    lines.append(f"<file path='{entry.path}'>")
    lines.extend(entry.content.splitlines())
    lines.append("</file>")


def _render_plain_entry(entry: Entry, lines: list[str]) -> None:
    lines.append(f"FILE: {entry.path}")
    lines.extend(entry.content.splitlines())


def _render_markdown_entry(entry: Entry, lines: list[str]) -> None:
    lines.append(f"### {entry.path}")
    lines.append("```")
    lines.extend(entry.content.splitlines())
    lines.append("```")


def build_output(session: Session) -> BuildResult:
    """Buduje finalny output ze stanu sesji."""
    lines: list[str] = []
    if session.prompt_text:
        lines.append(session.prompt_text)

    included = 0
    excluded = 0
    warnings: list[str] = []
    errors: list[str] = []

    for entry in session.entries:
        if entry.read_error:
            errors.append(f"{entry.path}: {entry.read_error}")
            excluded += 1
            continue
        if not entry.include_in_output:
            excluded += 1
            continue

        included += 1
        if session.output_format == OutputFormat.MARKDOWN:
            _render_markdown_entry(entry, lines)
        elif session.output_format == OutputFormat.PLAIN:
            _render_plain_entry(entry, lines)
        else:
            _render_xml_entry(entry, lines)

    _prompt_tokens, _attachment_tokens, total = count_session_tokens(session)
    return BuildResult(
        rendered_output="\n".join(lines),
        total_tokens=total,
        included_entries=included,
        excluded_entries=excluded,
        warnings=warnings,
        errors=errors,
    )

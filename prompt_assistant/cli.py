"""Minimalny CLI hook dla PromptGlue."""
from __future__ import annotations

import argparse
from pathlib import Path

from prompt_assistant.core import EntrySourceType, OutputFormat, Session, add_entry, build_output, create_entry


def render_from_sources(
    prompt_text: str,
    sources: list[tuple[str, str]],
    output_format: OutputFormat = OutputFormat.XML,
) -> str:
    """Renderuje finalny output na podstawie podanych źródeł tekstu."""
    session = Session(prompt_text=prompt_text, output_format=output_format)
    for path, content in sources:
        entry = create_entry(path=path, source_type=EntrySourceType.FILE, content=content)
        add_entry(session, entry)
    return build_output(session).rendered_output


def _parse_output_format(value: str) -> OutputFormat:
    normalized = value.strip().lower()
    if normalized == "markdown":
        return OutputFormat.MARKDOWN
    if normalized == "plain":
        return OutputFormat.PLAIN
    return OutputFormat.XML


def main() -> None:
    parser = argparse.ArgumentParser(description="PromptGlue CLI (minimal hook)")
    parser.add_argument("files", nargs="*", help="Ścieżki plików do dołączenia")
    parser.add_argument("--prompt", default="", help="Treść promptu")
    parser.add_argument(
        "--format",
        default="xml",
        choices=["xml", "markdown", "plain"],
        help="Profil outputu",
    )
    parser.add_argument("--output", default="", help="Plik wyjściowy (opcjonalnie)")

    args = parser.parse_args()

    sources: list[tuple[str, str]] = []
    for path_str in args.files:
        path = Path(path_str)
        if not path.is_file():
            raise SystemExit(f"Nie znaleziono pliku: {path}")
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SystemExit(f"Błąd odczytu {path}: {exc}") from exc
        sources.append((str(path), content))

    rendered = render_from_sources(args.prompt, sources, _parse_output_format(args.format))

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
        return

    print(rendered)


if __name__ == "__main__":
    main()

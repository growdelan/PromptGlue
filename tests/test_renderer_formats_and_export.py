"""Testy dla profili renderowania i eksportu (M2)."""
from __future__ import annotations

import unittest
from unittest.mock import mock_open, patch

from prompt_assistant.core import EntrySourceType, OutputFormat, Session, add_entry, build_output, create_entry
from prompt_assistant.exporter import export_text_to_file


class RendererFormatsAndExportTests(unittest.TestCase):
    def _build_sample_session(self, output_format: OutputFormat) -> Session:
        session = Session(prompt_text="Instrukcja", output_format=output_format)
        entry = create_entry("src/main.py", EntrySourceType.FILE, "print('hello')")
        add_entry(session, entry)
        return session

    def test_xml_like_profile(self) -> None:
        result = build_output(self._build_sample_session(OutputFormat.XML))
        self.assertIn("<file path='src/main.py'>", result.rendered_output)
        self.assertIn("</file>", result.rendered_output)

    def test_markdown_profile(self) -> None:
        result = build_output(self._build_sample_session(OutputFormat.MARKDOWN))
        self.assertIn("### src/main.py", result.rendered_output)
        self.assertIn("```", result.rendered_output)

    def test_plain_text_profile(self) -> None:
        result = build_output(self._build_sample_session(OutputFormat.PLAIN))
        self.assertIn("FILE: src/main.py", result.rendered_output)
        self.assertNotIn("<file path='src/main.py'>", result.rendered_output)

    def test_export_writes_utf8_file(self) -> None:
        mocked_open = mock_open()
        with patch("builtins.open", mocked_open):
            export_text_to_file("wynik.md", "abc")

        mocked_open.assert_called_once_with("wynik.md", "w", encoding="utf-8")
        mocked_open.return_value.__enter__.return_value.write.assert_called_once_with("abc")


if __name__ == "__main__":
    unittest.main()

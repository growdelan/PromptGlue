"""Testy minimalnego hooka CLI (M4)."""
from __future__ import annotations

import unittest

from prompt_assistant.cli import render_from_sources
from prompt_assistant.core import OutputFormat


class CliHookTests(unittest.TestCase):
    def test_render_from_sources_xml(self) -> None:
        output = render_from_sources(
            "Instrukcja",
            [("a.py", "print('a')"), ("b.py", "print('b')")],
            OutputFormat.XML,
        )
        self.assertIn("Instrukcja", output)
        self.assertIn("<file path='a.py'>", output)
        self.assertIn("<file path='b.py'>", output)

    def test_render_from_sources_plain(self) -> None:
        output = render_from_sources(
            "",
            [("a.py", "print('a')")],
            OutputFormat.PLAIN,
        )
        self.assertIn("FILE: a.py", output)
        self.assertNotIn("<file path='a.py'>", output)


if __name__ == "__main__":
    unittest.main()

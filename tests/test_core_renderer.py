"""Testy regresyjne dla warstwy core (M1)."""
from __future__ import annotations

import unittest

from prompt_assistant.core import (
    EntrySourceType,
    Session,
    add_entry,
    build_output,
    create_entry,
    remove_entry,
    set_entry_inclusion,
)


class CoreRendererTests(unittest.TestCase):
    def test_removed_file_is_not_rendered(self) -> None:
        session = Session(prompt_text="Instrukcja")
        file_a = create_entry("a.py", EntrySourceType.FILE, "print('a')")
        file_b = create_entry("b.py", EntrySourceType.FILE, "print('b')")
        add_entry(session, file_a)
        add_entry(session, file_b)

        removed = remove_entry(session, file_b.entry_id)
        self.assertTrue(removed)

        result = build_output(session)
        self.assertIn("<file path='a.py'>", result.rendered_output)
        self.assertNotIn("<file path='b.py'>", result.rendered_output)

    def test_excluded_file_is_not_rendered(self) -> None:
        session = Session(prompt_text="Instrukcja")
        file_a = create_entry("a.py", EntrySourceType.FILE, "print('a')")
        file_b = create_entry("b.py", EntrySourceType.FILE, "print('b')")
        add_entry(session, file_a)
        add_entry(session, file_b)

        changed = set_entry_inclusion(session, file_b.entry_id, False)
        self.assertTrue(changed)

        result = build_output(session)
        self.assertIn("<file path='a.py'>", result.rendered_output)
        self.assertNotIn("<file path='b.py'>", result.rendered_output)
        self.assertEqual(result.included_entries, 1)
        self.assertEqual(result.excluded_entries, 1)

    def test_render_order_is_deterministic(self) -> None:
        session = Session(prompt_text="Instrukcja")
        first = create_entry("first.txt", EntrySourceType.FILE, "1")
        second = create_entry("second.txt", EntrySourceType.FILE, "2")
        add_entry(session, first)
        add_entry(session, second)

        result = build_output(session)
        first_index = result.rendered_output.find("<file path='first.txt'>")
        second_index = result.rendered_output.find("<file path='second.txt'>")

        self.assertGreaterEqual(first_index, 0)
        self.assertGreaterEqual(second_index, 0)
        self.assertLess(first_index, second_index)


if __name__ == "__main__":
    unittest.main()

"""Regression tests for directory tree sync with exclude/remove."""
from __future__ import annotations

import unittest

from prompt_assistant.core import EntrySourceType, Session, add_entry, create_entry, get_entry
from prompt_assistant.gui.controllers import _sync_directory_tree_entries


class _DummyWindow:
    def __init__(self) -> None:
        self.session = Session()
        self.attached_dirs = []


class DirectoryTreeSyncTests(unittest.TestCase):
    def test_tree_content_excludes_excluded_files(self) -> None:
        window = _DummyWindow()

        tree_entry = create_entry("repo/.tree", EntrySourceType.DIRECTORY_TREE, ".")
        add_entry(window.session, tree_entry)

        file_a = create_entry("a.py", EntrySourceType.DIRECTORY_FILE, "print('a')")
        file_b = create_entry("b.py", EntrySourceType.DIRECTORY_FILE, "print('b')")
        add_entry(window.session, file_a)
        add_entry(window.session, file_b)

        window.attached_dirs.append(
            {
                "name": "repo",
                "tree": ".",
                "tree_entry_id": tree_entry.entry_id,
                "files": [
                    {"rel": "a.py", "excluded": False},
                    {"rel": "b.py", "excluded": True},
                ],
            }
        )

        _sync_directory_tree_entries(window)

        updated_tree = get_entry(window.session, tree_entry.entry_id)
        self.assertIsNotNone(updated_tree)
        self.assertIn("a.py", updated_tree.content)
        self.assertNotIn("b.py", updated_tree.content)

    def test_tree_is_disabled_when_all_files_excluded(self) -> None:
        window = _DummyWindow()

        tree_entry = create_entry("repo/.tree", EntrySourceType.DIRECTORY_TREE, ".")
        add_entry(window.session, tree_entry)

        file_a = create_entry("a.py", EntrySourceType.DIRECTORY_FILE, "print('a')")
        add_entry(window.session, file_a)

        window.attached_dirs.append(
            {
                "name": "repo",
                "tree": ".",
                "tree_entry_id": tree_entry.entry_id,
                "files": [
                    {"rel": "a.py", "excluded": True},
                ],
            }
        )

        _sync_directory_tree_entries(window)

        updated_tree = get_entry(window.session, tree_entry.entry_id)
        self.assertIsNotNone(updated_tree)
        self.assertEqual(updated_tree.content, ".")
        self.assertFalse(updated_tree.include_in_output)


if __name__ == "__main__":
    unittest.main()

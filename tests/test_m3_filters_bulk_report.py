"""Testy Milestone 3: filtry, masowe akcje i raporty."""
from __future__ import annotations

import unittest

from prompt_assistant.core import (
    EntrySourceType,
    FileListRecord,
    Session,
    add_entry,
    build_import_report,
    create_entry,
    exclude_entries,
    include_entries,
    matches_filters,
    remove_entries,
)


class M3FiltersBulkReportTests(unittest.TestCase):
    def test_matches_filters_by_name_extension_and_status(self) -> None:
        record = FileListRecord(display_name="repo/src/main.py", extension=".py", status="active")

        self.assertTrue(
            matches_filters(
                record,
                name_query="main",
                extension_query="py",
                status_filter="active",
            )
        )
        self.assertFalse(
            matches_filters(
                record,
                name_query="main",
                extension_query="md",
                status_filter="active",
            )
        )
        self.assertFalse(
            matches_filters(
                record,
                name_query="readme",
                extension_query="py",
                status_filter="active",
            )
        )

    def test_bulk_include_exclude_and_remove(self) -> None:
        session = Session()
        a = create_entry("a.py", EntrySourceType.FILE, "a")
        b = create_entry("b.py", EntrySourceType.FILE, "b")
        c = create_entry("c.py", EntrySourceType.FILE, "c")
        add_entry(session, a)
        add_entry(session, b)
        add_entry(session, c)

        excluded = exclude_entries(session, [a.entry_id, b.entry_id])
        self.assertEqual(excluded, 2)
        self.assertFalse(a.include_in_output)
        self.assertFalse(b.include_in_output)

        included = include_entries(session, [a.entry_id])
        self.assertEqual(included, 1)
        self.assertTrue(a.include_in_output)

        removed = remove_entries(session, [c.entry_id])
        self.assertEqual(removed, 1)
        self.assertEqual(len(session.entries), 2)

    def test_import_report_contains_reasons(self) -> None:
        report = build_import_report(
            added_count=5,
            skipped_git=2,
            skipped_custom=1,
            skipped_binary=3,
            read_errors=["a.py: Permission denied", "b.py: Decode error"],
        )

        self.assertIn("Dodano: 5", report)
        self.assertIn("Pominięto .gitignore: 2", report)
        self.assertIn("Pominięto custom: 1", report)
        self.assertIn("Pominięto binarne: 3", report)
        self.assertIn("Błędy odczytu: 2", report)
        self.assertIn("a.py: Permission denied", report)


if __name__ == "__main__":
    unittest.main()

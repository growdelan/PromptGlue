"""Controller logic (event handlers) for PromptAssistantWindow."""
from __future__ import annotations

import os
from typing import Dict, List

import pathspec
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QGuiApplication
from PyQt5.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPlainTextEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
)

from prompt_assistant.config import MAX_DIR_SIZE, WARNING_TOKEN_LIMIT, CRITICAL_TOKEN_LIMIT
from prompt_assistant.core import (
    EntrySourceType,
    FileListRecord,
    OutputFormat,
    add_entry,
    build_import_report,
    build_output,
    clear_session,
    count_entry_tokens,
    count_session_tokens,
    create_entry,
    exclude_entries,
    get_entry,
    include_entries,
    matches_filters,
    remove_entry,
    set_entry_inclusion,
)
from prompt_assistant.exporter import export_text_to_file
from prompt_assistant.utils import render_tree_structure, is_binary, build_gitignore_spec
from .ui import PromptAssistantWindow
from .preview_dialog import FilePreviewDialog


def _sync_prompt_text(window: PromptAssistantWindow) -> None:
    window.session.prompt_text = window.text_edit.toPlainText()


def _get_file_status(file_obj: dict) -> str:
    if file_obj.get("read_error"):
        return "error"
    if file_obj.get("excluded"):
        return "excluded"
    return "active"


def _refresh_item_visual(item: QListWidgetItem, file_obj: dict) -> None:
    status = _get_file_status(file_obj)
    display_name = file_obj.get("display_name") or file_obj.get("name") or file_obj.get("rel") or "plik"

    if status == "error":
        error_text = file_obj.get("read_error", "nieznany błąd")
        item.setText(f"{display_name} [error: {error_text}]")
    elif status == "excluded":
        item.setText(f"{display_name} [excluded]")
    else:
        item.setText(display_name)

    font: QFont = item.font()
    font.setStrikeOut(status in ("excluded", "error"))
    item.setFont(font)


def _sync_directory_tree_entries(window: PromptAssistantWindow) -> None:
    """Synchronizuje include tree-entry katalogu na podstawie stanu jego plików."""
    dirs_to_remove: List[dict] = []
    for directory in window.attached_dirs:
        if not directory["files"]:
            remove_entry(window.session, directory["tree_entry_id"])
            dirs_to_remove.append(directory)
            continue

        has_active_files = any(_get_file_status(f) == "active" for f in directory["files"])
        set_entry_inclusion(window.session, directory["tree_entry_id"], has_active_files)

    for directory in dirs_to_remove:
        window.attached_dirs.remove(directory)


def _build_current_output(window: PromptAssistantWindow):
    _sync_prompt_text(window)
    _sync_directory_tree_entries(window)
    return build_output(window.session)


# --------------------------------------------------------------------------- UI

def _update_token_label(window: PromptAssistantWindow) -> None:
    """Przelicza tokeny promptu i załączników z pominięciem wykluczonych plików."""
    _sync_prompt_text(window)
    _sync_directory_tree_entries(window)

    prompt_tokens, attach_tokens, total = count_session_tokens(window.session)
    window.prompt_tokens = prompt_tokens
    window.attachments_tokens = attach_tokens
    window.total_tokens = total

    window.token_label.setText(
        f"Tokeny: prompt: {window.prompt_tokens} | pliki: {attach_tokens} | suma: {total}"
    )
    if total > CRITICAL_TOKEN_LIMIT:
        window.token_label.setStyleSheet("color: red; font-weight: bold")
    elif total > WARNING_TOKEN_LIMIT:
        window.token_label.setStyleSheet("color: orange; font-weight: bold")
    else:
        window.token_label.setStyleSheet("")


def _toggle_gitignore(window: PromptAssistantWindow, state: int) -> None:
    window.ignore_gitignored = state == Qt.Checked


# -------------------------------------------------------------------- helpers --

def _create_file_item(
    window: PromptAssistantWindow,
    file_obj: dict,
    is_dir_file: bool = False,
) -> None:
    """Dodaje wpis do QListWidget i przypina obiekt pliku w UserRole."""
    item = QListWidgetItem(file_obj["display_name"])
    item.setData(Qt.UserRole, ("dir_file" if is_dir_file else "file", file_obj))
    _refresh_item_visual(item, file_obj)
    window.files_list.addItem(item)


def _create_file_entry(path: str, content: str, source_type: EntrySourceType, *, read_error: str | None = None):
    size = len(content.encode("utf-8"))
    return create_entry(
        path=path,
        source_type=source_type,
        content=content,
        size=size,
        include_in_output=(read_error is None),
        read_error=read_error,
    )


def _iter_file_items(window: PromptAssistantWindow):
    for idx in range(window.files_list.count()):
        item = window.files_list.item(idx)
        role = item.data(Qt.UserRole)
        if not role:
            continue
        kind, file_obj = role
        if kind in ("file", "dir_file"):
            yield item, file_obj


# --------------------------------------------------------------------- filters

def apply_list_filters(window: PromptAssistantWindow) -> None:
    """Filtruje listę plików po nazwie, rozszerzeniu i statusie."""
    name_query = window.name_filter_edit.text()
    extension_query = window.ext_filter_edit.text()
    status_filter = window.status_filter_combo.currentData() or "all"

    for item, file_obj in _iter_file_items(window):
        extension = file_obj.get("extension", "")
        record = FileListRecord(
            display_name=file_obj.get("display_name", ""),
            extension=extension,
            status=_get_file_status(file_obj),
        )
        visible = matches_filters(
            record,
            name_query=name_query,
            extension_query=extension_query,
            status_filter=status_filter,
        )
        item.setHidden(not visible)


# --------------------------------------------------------------------- actions

def attach_files(window: PromptAssistantWindow) -> None:
    paths, _ = QFileDialog.getOpenFileNames(window, "Wybierz pliki...", "", "*.*")
    read_errors: List[str] = []

    for path in paths:
        if not os.path.isfile(path):
            continue

        name = os.path.basename(path)
        extension = os.path.splitext(name)[1].lower()

        try:
            with open(path, encoding="utf-8") as file_handle:
                content = file_handle.read()
            entry = _create_file_entry(name, content, EntrySourceType.FILE)
            add_entry(window.session, entry)
            file_obj = {
                "name": name,
                "display_name": name,
                "content": content,
                "excluded": False,
                "entry_id": entry.entry_id,
                "extension": extension,
                "read_error": None,
            }
        except Exception as exc:
            error_text = str(exc)
            entry = _create_file_entry(name, "", EntrySourceType.FILE, read_error=error_text)
            add_entry(window.session, entry)
            file_obj = {
                "name": name,
                "display_name": name,
                "content": "",
                "excluded": True,
                "entry_id": entry.entry_id,
                "extension": extension,
                "read_error": error_text,
            }
            read_errors.append(f"{name}: {error_text}")

        window.attached_files.append(file_obj)
        _create_file_item(window, file_obj)

    if read_errors:
        QMessageBox.warning(window, "Błędy odczytu plików", "\n".join(read_errors))

    _update_token_label(window)
    apply_list_filters(window)


def attach_directory(window: PromptAssistantWindow) -> None:
    dir_path = QFileDialog.getExistingDirectory(window, "Wybierz katalog...", "")
    if not dir_path:
        return

    total_size = 0
    for root, dirs, files in os.walk(dir_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for filename in files:
            try:
                total_size += os.path.getsize(os.path.join(root, filename))
            except OSError:
                pass
        if total_size > MAX_DIR_SIZE:
            QMessageBox.warning(window, "Zbyt duży katalog", f"{os.path.basename(dir_path)} > 1 GB")
            return

    git_spec = build_gitignore_spec(dir_path) if window.ignore_gitignored else None
    custom = [pattern.strip() for pattern in window.exclude_edit.text().split(",") if pattern.strip()]
    custom_spec = pathspec.PathSpec.from_lines("gitwildmatch", custom) if custom else None

    collected: List[Dict] = []
    skipped = {"binary": 0, "git": 0, "custom": 0}
    read_errors: List[str] = []
    base = len(dir_path) + 1

    for root, dirs, files in os.walk(dir_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for filename in files:
            full = os.path.join(root, filename)
            rel = full[base:].replace(os.sep, "/")

            if git_spec and git_spec.match_file(rel):
                skipped["git"] += 1
                continue
            if custom_spec and custom_spec.match_file(rel):
                skipped["custom"] += 1
                continue
            if is_binary(full):
                skipped["binary"] += 1
                continue

            try:
                with open(full, encoding="utf-8") as file_handle:
                    content = file_handle.read()
                collected.append(
                    {
                        "rel": rel,
                        "display_name": f"{os.path.basename(dir_path)}/{rel}",
                        "content": content,
                        "excluded": False,
                        "extension": os.path.splitext(rel)[1].lower(),
                        "read_error": None,
                    }
                )
            except Exception as exc:
                read_errors.append(f"{rel}: {exc}")

    if not collected:
        report = build_import_report(
            added_count=0,
            skipped_git=skipped["git"],
            skipped_custom=skipped["custom"],
            skipped_binary=skipped["binary"],
            read_errors=read_errors,
        )
        QMessageBox.information(window, "Brak plików", report)
        return

    tree = render_tree_structure([file_item["rel"] for file_item in collected])
    name = os.path.basename(dir_path)

    tree_entry = _create_file_entry(f"{name}/.tree", tree, EntrySourceType.DIRECTORY_TREE)
    add_entry(window.session, tree_entry)

    for file_item in collected:
        entry = _create_file_entry(file_item["rel"], file_item["content"], EntrySourceType.DIRECTORY_FILE)
        add_entry(window.session, entry)
        file_item["entry_id"] = entry.entry_id

    window.attached_dirs.append(
        {
            "name": name,
            "files": collected,
            "tree": tree,
            "tree_entry_id": tree_entry.entry_id,
        }
    )

    for file_item in collected:
        _create_file_item(window, file_item, is_dir_file=True)

    report = build_import_report(
        added_count=len(collected),
        skipped_git=skipped["git"],
        skipped_custom=skipped["custom"],
        skipped_binary=skipped["binary"],
        read_errors=read_errors,
    )
    QMessageBox.information(window, "Raport importu katalogu", report)

    _update_token_label(window)
    apply_list_filters(window)


def copy_text(window: PromptAssistantWindow) -> None:
    """Buduje finalny output i kopiuje do clipboard."""
    result = _build_current_output(window)
    QGuiApplication.clipboard().setText(result.rendered_output)


def set_output_format(window: PromptAssistantWindow, _index: int) -> None:
    """Ustawia format renderowania outputu według wyboru użytkownika."""
    format_value = window.output_format_combo.currentData()
    if format_value == OutputFormat.MARKDOWN.value:
        window.session.output_format = OutputFormat.MARKDOWN
    elif format_value == OutputFormat.PLAIN.value:
        window.session.output_format = OutputFormat.PLAIN
    else:
        window.session.output_format = OutputFormat.XML


def export_text(window: PromptAssistantWindow, output_text: str | None = None) -> bool:
    """Eksportuje wynik do pliku `.md` lub `.txt`."""
    text_to_export = output_text if output_text is not None else _build_current_output(window).rendered_output
    if not text_to_export:
        QMessageBox.information(window, "Brak danych", "Brak treści do eksportu.")
        return False

    default_ext = ".txt" if window.session.output_format == OutputFormat.PLAIN else ".md"
    path, _ = QFileDialog.getSaveFileName(
        window,
        "Eksportuj wynik",
        f"prompt_output{default_ext}",
        "Markdown (*.md);;Text (*.txt)",
    )
    if not path:
        return False

    if not path.endswith(".md") and not path.endswith(".txt"):
        path = f"{path}{default_ext}"

    try:
        export_text_to_file(path, text_to_export)
    except OSError as exc:
        QMessageBox.critical(window, "Błąd eksportu", f"Nie udało się zapisać pliku: {exc}")
        return False

    QMessageBox.information(window, "Eksport zakończony", f"Zapisano plik: {path}")
    return True


def preview_final_output(window: PromptAssistantWindow) -> None:
    """Pokazuje finalny output używany przez copy/export."""
    result = _build_current_output(window)

    dialog = QDialog(window)
    dialog.setWindowTitle("Final preview")
    dialog.setMinimumWidth(860)
    dialog.setMinimumHeight(620)
    layout = QVBoxLayout(dialog)

    summary = QLabel(
        f"Tokeny łącznie: {result.total_tokens} | "
        f"Uwzględnione wpisy: {result.included_entries} | "
        f"Pominięte wpisy: {result.excluded_entries}"
    )
    layout.addWidget(summary)

    text = QPlainTextEdit(result.rendered_output)
    text.setReadOnly(True)
    layout.addWidget(text)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch(1)

    btn_copy = QPushButton("Copy")
    btn_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(text.toPlainText()))
    btn_layout.addWidget(btn_copy)

    btn_export = QPushButton("Export")
    btn_export.clicked.connect(lambda: export_text(window, text.toPlainText()))
    btn_layout.addWidget(btn_export)

    btn_close = QPushButton("Close")
    btn_close.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_close)

    layout.addLayout(btn_layout)
    dialog.exec_()


def _selected_file_items(window: PromptAssistantWindow) -> list[tuple[QListWidgetItem, dict]]:
    selected: list[tuple[QListWidgetItem, dict]] = []
    for item in window.files_list.selectedItems():
        role = item.data(Qt.UserRole)
        if not role:
            continue
        kind, file_obj = role
        if kind in ("file", "dir_file"):
            selected.append((item, file_obj))
    return selected


def bulk_include_selected(window: PromptAssistantWindow) -> None:
    selected = _selected_file_items(window)
    entry_ids = [file_obj["entry_id"] for _item, file_obj in selected if not file_obj.get("read_error")]
    include_entries(window.session, entry_ids)

    for item, file_obj in selected:
        if file_obj.get("read_error"):
            continue
        file_obj["excluded"] = False
        _refresh_item_visual(item, file_obj)

    _sync_directory_tree_entries(window)
    _update_token_label(window)
    apply_list_filters(window)


def bulk_exclude_selected(window: PromptAssistantWindow) -> None:
    selected = _selected_file_items(window)
    entry_ids = [file_obj["entry_id"] for _item, file_obj in selected if not file_obj.get("read_error")]
    exclude_entries(window.session, entry_ids)

    for item, file_obj in selected:
        if file_obj.get("read_error"):
            continue
        file_obj["excluded"] = True
        _refresh_item_visual(item, file_obj)

    _sync_directory_tree_entries(window)
    _update_token_label(window)
    apply_list_filters(window)


def bulk_remove_selected(window: PromptAssistantWindow) -> None:
    selected = _selected_file_items(window)
    for item, file_obj in selected:
        row = window.files_list.row(item)
        window.files_list.takeItem(row)
        remove_file_from_session(window, file_obj)

    _update_token_label(window)
    apply_list_filters(window)


def clear_all(window: PromptAssistantWindow) -> None:
    window.text_edit.clear()
    window.files_list.clear()
    window.attached_dirs.clear()
    window.attached_files.clear()
    clear_session(window.session)
    window.prompt_tokens = window.attachments_tokens = window.total_tokens = 0
    window.token_label.setText("Tokeny: prompt: 0 | pliki: 0 | suma: 0")


# ----------------------------------------------------------------- preview slot

def preview_file(window: PromptAssistantWindow, item: QListWidgetItem) -> None:
    """Obsługa podwójnego kliknięcia na element listy."""
    role = item.data(Qt.UserRole)
    if not role:
        return
    kind, file_obj = role
    if kind not in ("file", "dir_file"):
        return
    dialog = FilePreviewDialog(window, item, file_obj, is_dir_file=(kind == "dir_file"))
    dialog.exec_()


def remove_file_from_session(window: PromptAssistantWindow, file_obj: dict) -> None:
    """Usuwa wskazany plik z modeli GUI i z sesji core."""
    remove_entry(window.session, file_obj["entry_id"])

    if file_obj in window.attached_files:
        window.attached_files.remove(file_obj)
    else:
        for directory in window.attached_dirs:
            if file_obj in directory["files"]:
                directory["files"].remove(file_obj)
                break

    _sync_directory_tree_entries(window)


def show_token_distribution(window: PromptAssistantWindow) -> None:
    """Wyświetla modalne okno z rozkładem tokenów promptu i załączonych plików."""
    _sync_prompt_text(window)

    prompt_tokens, _attach_tokens, _total = count_session_tokens(window.session)

    file_counts: List[tuple[str, int]] = []
    for file_obj in window.attached_files:
        if _get_file_status(file_obj) != "active":
            continue
        entry = get_entry(window.session, file_obj["entry_id"])
        if entry is None:
            continue
        file_counts.append((file_obj["name"], count_entry_tokens(entry)))
    file_counts.sort(key=lambda item: item[1], reverse=True)

    dir_data: List[tuple[str, int, List[tuple[str, int]]]] = []
    for directory in window.attached_dirs:
        tree_entry = get_entry(window.session, directory["tree_entry_id"])
        tree_tokens = count_entry_tokens(tree_entry) if tree_entry else 0

        files: List[tuple[str, int]] = []
        for file_obj in directory["files"]:
            if _get_file_status(file_obj) != "active":
                continue
            entry = get_entry(window.session, file_obj["entry_id"])
            if entry is None:
                continue
            files.append((file_obj["rel"], count_entry_tokens(entry)))
        files.sort(key=lambda item: item[1], reverse=True)
        dir_data.append((directory["name"], tree_tokens, files))

    lines: List[str] = []
    lines.append("Prompt")
    lines.append(f"  prompt: {prompt_tokens} tokenów")
    lines.append("")
    if file_counts:
        lines.append("Pliki pojedyncze")
        for name, tokens in file_counts:
            lines.append(f"  {name}: {tokens} tokenów")
        lines.append("")
    if dir_data:
        lines.append("Katalogi")
        for dir_name, tree_tokens, files in dir_data:
            lines.append(f"{dir_name}")
            lines.append(f"  tree: {tree_tokens} tokenów")
            for rel, tokens in files:
                lines.append(f"  {rel}: {tokens} tokenów")
            lines.append("")
    report = "\n".join(lines)

    dialog = QDialog(window)
    dialog.setWindowTitle("Rozkład tokenów")
    dialog.setMinimumWidth(600)
    layout = QVBoxLayout(dialog)

    text = QPlainTextEdit(report)
    text.setReadOnly(True)
    layout.addWidget(text)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch(1)
    btn_close = QPushButton("Close")
    btn_close.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)

    dialog.exec_()


# ----------------------------------------------------------------------- setup

def setup_ui(window: PromptAssistantWindow) -> None:
    from .ui import build_ui

    build_ui(window)


def connect_signals(window: PromptAssistantWindow) -> None:
    from .ui import bind_signals

    bind_signals(window)

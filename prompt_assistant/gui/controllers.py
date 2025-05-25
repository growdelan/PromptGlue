"""Controller logic (event handlers) for PromptAssistantWindow."""
from __future__ import annotations

import os
from typing import List, Dict

import pathspec
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
)

from prompt_assistant.config import MAX_DIR_SIZE, WARNING_TOKEN_LIMIT, CRITICAL_TOKEN_LIMIT
from prompt_assistant.utils import (
    count_tokens,
    render_tree_structure,
    is_binary,
    build_gitignore_spec,
)
from .ui import PromptAssistantWindow
from .preview_dialog import FilePreviewDialog


# --------------------------------------------------------------------------- UI
def _update_token_label(window: PromptAssistantWindow) -> None:
    """Przelicza tokeny promptu i załączników z pominięciem wykluczonych plików."""
    prompt_text = window.text_edit.toPlainText()
    window.prompt_tokens = count_tokens(prompt_text) if prompt_text else 0

    attach_tokens = 0
    # --- pliki pojedyncze
    for f in window.attached_files:
        if not f["excluded"]:
            attach_tokens += count_tokens(f["content"])
    # --- pliki z katalogów
    for d in window.attached_dirs:
        attach_tokens += count_tokens(d["tree"])
        for f in d["files"]:
            if not f["excluded"]:
                attach_tokens += count_tokens(f["content"])

    window.attachments_tokens = attach_tokens
    total = window.prompt_tokens + attach_tokens
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


# -------------------------------------------------------------------- helpers –
def _create_file_item(
    window: PromptAssistantWindow,
    display_name: str,
    file_obj: dict,
    is_dir_file: bool = False,
) -> None:
    """Dodaje wpis do QListWidget i przypina obiekt pliku w UserRole."""
    item = QListWidgetItem(display_name)
    item.setData(Qt.UserRole, ("dir_file" if is_dir_file else "file", file_obj))
    lw = window.files_list
    lw.addItem(item)


# --------------------------------------------------------------------- actions
def attach_files(window: PromptAssistantWindow) -> None:
    paths, _ = QFileDialog.getOpenFileNames(window, "Wybierz pliki...", "", "*.*")
    for path in paths:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            name = os.path.basename(path)
            file_obj = {"name": name, "content": content, "excluded": False}
            window.attached_files.append(file_obj)
            _create_file_item(window, name, file_obj)
        except Exception:
            pass
    _update_token_label(window)


def attach_directory(window: PromptAssistantWindow) -> None:
    dir_path = QFileDialog.getExistingDirectory(window, "Wybierz katalog...", "")
    if not dir_path:
        return

    # --- Size sanity-check
    total_size = 0
    for root, dirs, files in os.walk(dir_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
        if total_size > MAX_DIR_SIZE:
            QMessageBox.warning(window, "Zbyt duży katalog", f"{os.path.basename(dir_path)} > 1 GB")
            return

    git_spec = build_gitignore_spec(dir_path) if window.ignore_gitignored else None
    custom = [p.strip() for p in window.exclude_edit.text().split(",") if p.strip()]
    custom_spec = pathspec.PathSpec.from_lines("gitwildmatch", custom) if custom else None

    collected: List[Dict] = []
    skipped = {"binary": 0, "git": 0, "custom": 0}
    base = len(dir_path) + 1

    for root, dirs, files in os.walk(dir_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            full = os.path.join(root, f)
            rel = full[base:].replace(os.sep, "/")
            # --- filters
            if git_spec and git_spec.match_file(rel):
                skipped["git"] += 1
                continue
            if custom_spec and custom_spec.match_file(rel):
                skipped["custom"] += 1
                continue
            if is_binary(full):
                skipped["binary"] += 1
                continue
            # --- collect
            try:
                with open(full, encoding="utf-8") as fh:
                    collected.append({"rel": rel, "content": fh.read(), "excluded": False})
            except Exception:
                skipped["binary"] += 1

    if not collected:
        QMessageBox.information(window, "Brak plików", "Nie znaleziono plików tekstowych.")
        return

    tree = render_tree_structure([f["rel"] for f in collected])
    name = os.path.basename(dir_path)
    window.attached_dirs.append({"name": name, "files": collected, "tree": tree})

    # --- UI items
    for f in collected:
        _create_file_item(window, f"{name}/{f['rel']}", f, is_dir_file=True)

    # --- info o pominieciach
    msgs = [f"{v} {k}" for k, v in skipped.items() if v]
    if msgs:
        QMessageBox.information(window, "Pominięto", ", ".join(msgs))

    _update_token_label(window)


def copy_text(window: PromptAssistantWindow) -> None:
    """Buduje prompt + wszystkie załączniki (bez excluded) i kopiuje do clipboard."""
    parts: List[str] = []
    p = window.text_edit.toPlainText()
    if p:
        parts.append(p)

    # --- katalogi
    for d in window.attached_dirs:
        parts.append("<directories>")
        parts.extend(d["tree"].splitlines())
        parts.append("</directories>")
        for f in d["files"]:
            if f["excluded"]:
                continue

            rel_path = f["rel"]
            if "/" in rel_path:
                tag_path = f"/{rel_path}"
            else:
                tag_path = rel_path

            parts.append(f"<file path='{tag_path}'>")
            parts.extend(f["content"].splitlines())
            parts.append(f"</file>")

    # --- pliki pojedyncze
    for f in window.attached_files:
        if f["excluded"]:
            continue
        parts.append(f"<file path='{f['name']}'>")
        parts.extend(f["content"].splitlines())
        parts.append(f"</file>")

    QGuiApplication.clipboard().setText("\n".join(parts))


def clear_all(window: PromptAssistantWindow) -> None:
    window.text_edit.clear()
    window.files_list.clear()
    window.attached_dirs.clear()
    window.attached_files.clear()
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
    dlg = FilePreviewDialog(window, item, file_obj, is_dir_file=(kind == "dir_file"))
    dlg.exec_()

def show_token_distribution(window: PromptAssistantWindow) -> None:
    """Wyświetla modalne okno z rozkładem tokenów promptu i załączonych plików."""
    # Dynamiczne liczenie
    prompt_text = window.text_edit.toPlainText() or ""
    prompt_tokens = count_tokens(prompt_text)

    # Pliki pojedyncze
    file_counts: List[tuple[str, int]] = [
        (f['name'], count_tokens(f['content']))
        for f in window.attached_files
        if not f['excluded']
    ]
    file_counts.sort(key=lambda x: x[1], reverse=True)

    # Katalogi
    dir_data: List[tuple[str, int, List[tuple[str, int]]]] = []
    for d in window.attached_dirs:
        tree_tokens = count_tokens(d['tree'])
        files = [
            (f['rel'], count_tokens(f['content']))
            for f in d['files']
            if not f['excluded']
        ]
        files.sort(key=lambda x: x[1], reverse=True)
        dir_data.append((d['name'], tree_tokens, files))

    # Budowanie raportu
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

    # Tworzenie dialogu
    dialog = QDialog(window)
    dialog.setWindowTitle("Rozkład tokenów")
    dialog.setMinimumWidth(600)
    layout = QVBoxLayout(dialog)

    # Raport w QPlainTextEdit
    text = QPlainTextEdit(report)
    text.setReadOnly(True)
    layout.addWidget(text)

    # Przyciski
    btn_layout = QHBoxLayout()
    btn_layout.addStretch(1)
    btn_close = QPushButton("Zamknij")
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
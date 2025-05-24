"""Controller logic (event handlers) for PromptAssistantWindow."""
from __future__ import annotations

import os

import pathspec
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox

from prompt_assistant.config import MAX_DIR_SIZE, WARNING_TOKEN_LIMIT, CRITICAL_TOKEN_LIMIT
from prompt_assistant.utils import (
    count_tokens,
    render_tree_structure,
    is_binary,
    build_gitignore_spec,
)
from .ui import PromptAssistantWindow


def _update_token_label(window: PromptAssistantWindow) -> None:
    prompt_text = window.text_edit.toPlainText()
    window.prompt_tokens = count_tokens(prompt_text) if prompt_text else 0

    attach_tokens = 0
    for _name, content in window.attached_files:
        attach_tokens += count_tokens(content)
    for d in window.attached_dirs:
        attach_tokens += count_tokens(d["tree"])
        for _rel, content in d["files"]:
            attach_tokens += count_tokens(content)
    window.attachments_tokens = attach_tokens

    total = window.prompt_tokens + window.attachments_tokens
    window.total_tokens = total
    window.token_label.setText(
        f"Tokeny: prompt: {window.prompt_tokens} | pliki: {window.attachments_tokens} | suma: {total}"
    )
    if total > CRITICAL_TOKEN_LIMIT:
        window.token_label.setStyleSheet("color: red; font-weight: bold")
    elif total > WARNING_TOKEN_LIMIT:
        window.token_label.setStyleSheet("color: orange; font-weight: bold")
    else:
        window.token_label.setStyleSheet("")


def _toggle_gitignore(window: PromptAssistantWindow, state: int) -> None:
    window.ignore_gitignored = state == Qt.Checked


def attach_files(window: PromptAssistantWindow) -> None:
    paths, _ = QFileDialog.getOpenFileNames(window, "Wybierz pliki...", "", "*.*")
    for path in paths:
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                name = os.path.basename(path)
                window.attached_files.append((name, content))
                window.files_list.addItem(QListWidgetItem(name))
            except Exception:
                pass
    _update_token_label(window)


def attach_directory(window: PromptAssistantWindow) -> None:
    dir_path = QFileDialog.getExistingDirectory(window, "Wybierz katalog...", "")
    if not dir_path:
        return
    # size check
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
            QMessageBox.warning(window, "Zbyt duży katalog", f"{os.path.basename(dir_path)} > 1 GB")
            return
    git_spec = build_gitignore_spec(dir_path) if window.ignore_gitignored else None
    custom = [p.strip() for p in window.exclude_edit.text().split(',') if p.strip()]
    custom_spec = pathspec.PathSpec.from_lines('gitwildmatch', custom) if custom else None

    collected = []
    skipped = {'binary':0, 'git':0, 'custom':0}
    base = len(dir_path)+1
    for root, dirs, files in os.walk(dir_path):
        if ".git" in dirs: dirs.remove(".git")
        for f in files:
            full = os.path.join(root, f)
            rel = full[base:].replace(os.sep,'/')
            if git_spec and git_spec.match_file(rel): skipped['git']+=1; continue
            if custom_spec and custom_spec.match_file(rel): skipped['custom']+=1; continue
            if is_binary(full): skipped['binary']+=1; continue
            try:
                with open(full, encoding="utf-8") as fh:
                    collected.append((rel, fh.read()))
            except Exception:
                skipped['binary']+=1
    if not collected:
        QMessageBox.information(window, "Brak plików", "Nie znaleziono plików tekstowych.")
        return
    tree = render_tree_structure([r for r,_ in collected])
    name = os.path.basename(dir_path)
    window.attached_dirs.append({'name':name,'files':collected,'tree':tree})
    item = QListWidgetItem(f"[DIR] {name} ({len(collected)})")
    window.files_list.addItem(item)
    msgs = [f"{v} {k}" for k,v in skipped.items() if v]
    if msgs: QMessageBox.information(window,"Pominięto",", ".join(msgs))
    _update_token_label(window)


def copy_text(window: PromptAssistantWindow) -> None:
    parts=[]
    p=window.text_edit.toPlainText()
    for d in window.attached_dirs:
        parts.append("<directories>")
        parts.extend(d['tree'].splitlines())
        parts.append("</directories>")
        for r,c in d['files']:
            parts.append(f"<file={d['name']}/{r}>")
            parts.extend(c.splitlines())
            parts.append(f"</file={d['name']}/{r}>")
    for n,c in window.attached_files:
        parts.append(f"<file={n}>")
        parts.extend(c.splitlines())
        parts.append(f"</file={n}>")
    QGuiApplication.clipboard().setText(p+"\n"+"\n".join(parts))


def clear_all(window: PromptAssistantWindow) -> None:
    window.text_edit.clear()
    window.files_list.clear()
    window.attached_dirs.clear()
    window.attached_files.clear()
    window.prompt_tokens=window.attachments_tokens=window.total_tokens=0
    window.token_label.setText("Tokeny: prompt: 0 | pliki: 0 | suma: 0")


def setup_ui(window: PromptAssistantWindow) -> None:
    from .ui import build_ui
    build_ui(window)


def connect_signals(window: PromptAssistantWindow) -> None:
    from .ui import bind_signals
    bind_signals(window)

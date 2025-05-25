'''File preview & management dialog.'''  
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QCheckBox,
    QListWidgetItem,
)

from prompt_assistant.utils import count_tokens

class FilePreviewDialog(QDialog):
    """QDialog pokazujący zawartość pliku z opcją wykluczenia lub usunięcia."""

    def __init__(
        self,
        window,                # główne okno – potrzebne do odświeżenia stanu
        list_item: QListWidgetItem,  # odpowiadający wpis w QListWidget
        file_obj: dict,        # słownik pliku {'name'/ 'rel', 'content', 'excluded'}
        is_dir_file: bool,     # czy plik pochodzi z katalogu
        parent=None,
    ) -> None:
        super().__init__(parent or window)
        self.setWindowTitle(file_obj.get("name", file_obj.get("rel")))
        self.setMinimumWidth(640)
        self.window = window
        self.list_item = list_item
        self.file_obj = file_obj
        self.is_dir_file = is_dir_file

        # ---- UI ----------------------------------------------------------------
        vbox = QVBoxLayout(self)

        header = QLabel(
            f"{self.window.windowTitle().split('—')[0]} — "
            f"{file_obj.get('name', file_obj.get('rel'))} "
            f"— {count_tokens(file_obj['content'])} tokenów"
        )
        header.setWordWrap(True)
        vbox.addWidget(header)

        self.viewer = QPlainTextEdit(file_obj["content"])
        self.viewer.setReadOnly(True)
        vbox.addWidget(self.viewer, 1)

        self.exclude_cb = QCheckBox("✅ Wyklucz ten plik z promptu")
        self.exclude_cb.setChecked(file_obj["excluded"])
        self.exclude_cb.stateChanged.connect(self._toggle_exclude)
        vbox.addWidget(self.exclude_cb)

        # ---- Buttons -----------------------------------------------------------
        hbox = QHBoxLayout()
        self.delete_btn = QPushButton("❌ Usuń plik z listy")
        self.delete_btn.clicked.connect(self._delete_file)
        self.close_btn = QPushButton("Zamknij")
        self.close_btn.clicked.connect(self.accept)
        hbox.addStretch(1)
        hbox.addWidget(self.delete_btn)
        hbox.addWidget(self.close_btn)
        vbox.addLayout(hbox)

    # --------------------------------------------------------------------- slots
    def _toggle_exclude(self, state: int) -> None:
        """Aktualizuje status excluded i formatowanie w liście."""
        # Late import to avoid circular import
        from prompt_assistant.gui.controllers import _update_token_label

        self.file_obj["excluded"] = state == Qt.Checked
        font: QFont = self.list_item.font()
        font.setStrikeOut(self.file_obj["excluded"])
        self.list_item.setFont(font)
        _update_token_label(self.window)

    def _delete_file(self) -> None:
        """Usuwa plik ze wszystkich struktur + z UI."""
        # Late import to avoid circular import
        from prompt_assistant.gui.controllers import _update_token_label

        lw = self.window.files_list
        row = lw.row(self.list_item)
        lw.takeItem(row)

        # Usuń z modelu
        if self.file_obj in self.window.attached_files:
            self.window.attached_files.remove(self.file_obj)
        else:  # szukaj w katalogach
            for d in self.window.attached_dirs:
                if self.file_obj in d["files"]:
                    d["files"].remove(self.file_obj)
                    break

        _update_token_label(self.window)
        self.accept()

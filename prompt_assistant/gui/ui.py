"""UI construction and signal binding for PromptAssistantWindow."""
from __future__ import annotations

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QPlainTextEdit,
    QListWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QStatusBar,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)

__all__ = ["PromptAssistantWindow", "build_ui", "bind_signals"]


class PromptAssistantWindow(QMainWindow):
    """Main window for the Prompt Assistant GUI."""

    def __init__(self) -> None:
        super().__init__()
        # Initialize state
        self.attached_dirs = []   # [{'name', 'tree', 'files':[...]}]
        self.attached_files = []  # [{'name', 'content', 'excluded'}]
        self.prompt_tokens = 0
        self.attachments_tokens = 0
        self.total_tokens = 0
        self.ignore_gitignored = True

        build_ui(self)


def build_ui(window: PromptAssistantWindow) -> None:
    """Constructs the UI elements and layout on the given QMainWindow."""
    window.setWindowTitle("Pomocnik do tworzenia promptów")
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)

    layout.addWidget(QLabel("Wpisz treść promptu i załącz pliki lub katalogi:"))

    window.text_edit = QPlainTextEdit()
    window.text_edit.setPlaceholderText("Wpisz swój prompt…")
    layout.addWidget(window.text_edit)

    window.files_list = QListWidget()
    layout.addWidget(window.files_list)

    bar = QHBoxLayout()
    layout.addLayout(bar)

    window.attach_button = QPushButton("Załącz pliki")
    bar.addWidget(window.attach_button)

    window.attach_dir_button = QPushButton("Załącz katalog")
    bar.addWidget(window.attach_dir_button)

    window.exclude_edit = QLineEdit()
    window.exclude_edit.setPlaceholderText("Wykluczenia: *.md, README.txt…")
    bar.addWidget(window.exclude_edit, stretch=1)

    window.gitignore_checkbox = QCheckBox("Filtr .gitignore")
    window.gitignore_checkbox.setChecked(True)
    bar.addWidget(window.gitignore_checkbox)

    window.copy_button = QPushButton("Copy")
    bar.addWidget(window.copy_button)

    window.clear_button = QPushButton("Clear")
    bar.addWidget(window.clear_button)

    # Status bar & token label
    status = QStatusBar()
    window.setStatusBar(status)
    window.token_label = QLabel("Tokeny: prompt: 0 | pliki: 0 | suma: 0")
    status.addPermanentWidget(window.token_label)

    # Nowy przycisk: Pokaż rozkład tokenów
    window.show_token_dist_button = QPushButton("Pokaż rozkład tokenów")
    status.addPermanentWidget(window.show_token_dist_button)


def bind_signals(window: PromptAssistantWindow) -> None:
    """Connects UI events to controller functions."""
    from .controllers import (
        _update_token_label,
        _toggle_gitignore,
        attach_files,
        attach_directory,
        copy_text,
        clear_all,
        preview_file,
        show_token_distribution,
    )

    window.text_edit.textChanged.connect(lambda: _update_token_label(window))
    window.gitignore_checkbox.stateChanged.connect(lambda s: _toggle_gitignore(window, s))
    window.attach_button.clicked.connect(lambda: attach_files(window))
    window.attach_dir_button.clicked.connect(lambda: attach_directory(window))
    window.copy_button.clicked.connect(lambda: copy_text(window))
    window.clear_button.clicked.connect(lambda: clear_all(window))
    window.files_list.itemDoubleClicked.connect(lambda item: preview_file(window, item))
    window.show_token_dist_button.clicked.connect(lambda: show_token_distribution(window))
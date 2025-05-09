import sys
import os
import re
import pathspec
import tiktoken
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QCheckBox,
    QStatusBar,
)
from PyQt5.QtGui import QGuiApplication, QColor
from PyQt5.QtCore import Qt

# --- Stałe konfiguracyjne ----------------------------------------------------
MAX_DIR_SIZE = 1_000_000_000  # 1 GB
WARNING_TOKEN_LIMIT = 100_000  # Żółte ostrzeżenie
CRITICAL_TOKEN_LIMIT = 120_000  # Czerwone ostrzeżenie
MAX_TOKEN_LIMIT = 128_000  # GPT-4o limit


def count_tokens(text: str) -> int:
    """Liczy liczbę tokenów w tekście używając tokenizera GPT-4o."""
    encoder = tiktoken.get_encoding("cl100k_base")  # Tokenizer GPT-4o
    return len(encoder.encode(text))


class PromptAssistant(QMainWindow):
    """Główne okno aplikacji."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomocnik do tworzenia promptów")

        # --- Pamięć na załączniki -------------------------------------------
        self.attached_files = []  # list[tuple[nazwa, zawartość]]
        self.attached_dirs = []  # list[tuple[dir, list[tuple[rel_path, content]]]]

        # --- Liczniki tokenów -----------------------------------------------
        self.prompt_tokens = 0
        self.attachments_tokens = 0
        self.total_tokens = 0

        # --- UI --------------------------------------------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Dodanie paska statusu
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Etykieta z licznikiem tokenów
        self.token_label = QLabel("Tokeny: prompt: 0 | pliki: 0 | suma: 0")
        self.statusBar.addPermanentWidget(self.token_label)

        layout.addWidget(
            QLabel(
                "Wpisz treść promptu i załącz pliki lub katalogi, które chcesz do niego dodać:"
            )
        )

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Wpisz swój prompt...")
        layout.addWidget(self.text_edit)
        self.load_template()

        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.attach_button = QPushButton("Załącz pliki")
        self.attach_button.clicked.connect(self.attach_files)
        button_layout.addWidget(self.attach_button)

        self.attach_dir_button = QPushButton("Załącz katalog")
        self.attach_dir_button.clicked.connect(self.attach_directory)
        button_layout.addWidget(self.attach_dir_button)

        self.gitignore_checkbox = QCheckBox("Filtr .gitignore")
        self.gitignore_checkbox.setChecked(True)
        self.gitignore_checkbox.stateChanged.connect(self.toggle_ignore_gitignored)
        button_layout.addWidget(self.gitignore_checkbox)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

        self.ignore_gitignored = True  # domyślnie aktywne

        # Połącz sygnał textChanged z QTextEdit do aktualizacji licznika tokenów
        self.text_edit.textChanged.connect(self.update_token_count)

    def update_token_count(self):
        """Aktualizuje licznik tokenów dla promptu i załączników."""
        # Liczenie tokenów w promptcie
        prompt_text = self.text_edit.toPlainText()
        self.prompt_tokens = count_tokens(prompt_text) if prompt_text else 0

        # Liczenie tokenów w załącznikach
        self.attachments_tokens = 0

        # Załączone pliki
        for _, content in self.attached_files:
            self.attachments_tokens += count_tokens(content)

        # Załączone katalogi
        for _, files in self.attached_dirs:
            for _, content in files:
                self.attachments_tokens += count_tokens(content)

        # Suma tokenów
        self.total_tokens = self.prompt_tokens + self.attachments_tokens

        # Aktualizacja etykiety
        token_text = f"Tokeny: prompt: {self.prompt_tokens} | pliki: {self.attachments_tokens} | suma: {self.total_tokens}"
        self.token_label.setText(token_text)

        # Ustawienie kolorów ostrzeżeń
        if self.total_tokens > CRITICAL_TOKEN_LIMIT:
            self.token_label.setStyleSheet("color: red; font-weight: bold")
        elif self.total_tokens > WARNING_TOKEN_LIMIT:
            self.token_label.setStyleSheet("color: orange; font-weight: bold")
        else:
            self.token_label.setStyleSheet("")

    @staticmethod
    def sanitize_tag(name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

    @staticmethod
    def is_binary(path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.read(1024)
            return False
        except UnicodeDecodeError:
            return True

    @staticmethod
    def _build_gitignore_spec(root_dir: str):
        """
        Zbiera reguły ze wszystkich plików `.gitignore`
        w drzewie katalogu i zwraca pojedynczy PathSpec.
        Pomija puste linie i komentarze.
        """
        patterns = []
        for current_root, _, files in os.walk(root_dir):
            if ".gitignore" in files:
                gi_path = os.path.join(current_root, ".gitignore")
                try:
                    with open(gi_path, encoding="utf-8") as f:
                        for raw_line in f:
                            line = raw_line.strip()
                            # pomijamy puste linie i komentarze
                            if not line or line.startswith('#'):
                                continue
                            # dopasowujemy ścieżki względne względem root_dir
                            rel_base = os.path.relpath(current_root, root_dir).replace(os.sep, '/')
                            if rel_base != '.':
                                line = f"{rel_base}/{line}"
                            patterns.append(line)
                except OSError:
                    pass
        if patterns:
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        return None

    def load_template(self):
        self.text_edit.clear()
        self.text_edit.setPlaceholderText("Wpisz swój prompt...")

    def toggle_ignore_gitignored(self, state: int):
        self.ignore_gitignored = state == Qt.Checked

    def attach_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Wybierz pliki do załączenia", "", "Wszystkie pliki (*.*)"
        )
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    filename = os.path.basename(path)
                    self.attached_files.append((filename, content))
                    self.files_list.addItem(QListWidgetItem(filename))
                except Exception:
                    pass

        # Aktualizacja licznika tokenów po dodaniu plików
        self.update_token_count()

    def attach_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Wybierz katalog do załączenia", ""
        )
        if not dir_path:
            return

        total_size = 0
        for root, dirs, files in os.walk(dir_path):
            if ".git" in dirs:
                dirs.remove(".git")
            for fname in files:
                fp = os.path.join(root, fname)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
            if total_size > MAX_DIR_SIZE:
                QMessageBox.warning(
                    self,
                    "Zbyt duży katalog",
                    f"Katalog {os.path.basename(dir_path)} przekracza limit 1 GB i nie może zostać załadowany.",
                )
                return

        spec = None
        if self.ignore_gitignored:
            spec = self._build_gitignore_spec(dir_path)

        collected_files = []
        skipped_binary = 0
        skipped_ignored = 0
        root_len = len(dir_path) + 1

        for root, dirs, files in os.walk(dir_path):
            if ".git" in dirs:
                dirs.remove(".git")

            for fname in files:
                full = os.path.join(root, fname)
                rel = full[root_len:].replace(os.sep, "/")

                if spec and spec.match_file(rel):
                    skipped_ignored += 1
                    continue

                if self.is_binary(full):
                    skipped_binary += 1
                    continue
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        collected_files.append((rel, f.read()))
                except Exception:
                    skipped_binary += 1

        if not collected_files:
            QMessageBox.information(
                self,
                "Brak plików tekstowych",
                "Wybrany katalog nie zawiera plików tekstowych możliwych do wczytania.",
            )
            return

        dir_basename = os.path.basename(dir_path)
        self.attached_dirs.append((dir_basename, collected_files))

        item = QListWidgetItem(f"[DIR] {dir_basename} ({len(collected_files)} plików)")
        item.setForeground(Qt.blue)
        self.files_list.addItem(item)

        msgs = []
        if skipped_binary:
            msgs.append(f"{skipped_binary} plików binarnych lub nieobsługiwanych")
        if skipped_ignored:
            msgs.append(f"{skipped_ignored} plików na podstawie .gitignore")
        if msgs:
            QMessageBox.information(self, "Pominięto pliki", "Pominięto " + ", ".join(msgs) + ".")

        # Aktualizacja licznika tokenów po dodaniu katalogu
        self.update_token_count()

    def copy_text(self):
        user_text = self.text_edit.toPlainText()
        xml_parts = []

        if self.attached_files:
            xml_parts.append("<pliki>")
            for filename, content in self.attached_files:
                tag = self.sanitize_tag(filename)
                xml_parts.append(f"\t<{tag}>")
                for line in content.splitlines():
                    xml_parts.append(f"\t\t{line}")
                xml_parts.append(f"\t</{tag}>")
            xml_parts.append("</pliki>")

        for dirname, files in self.attached_dirs:
            dir_tag = self.sanitize_tag(dirname)
            xml_parts.append(f"<{dir_tag}>")
            for rel_path, content in files:
                file_tag = self.sanitize_tag(rel_path)
                xml_parts.append(f"\t<{file_tag}>")
                for line in content.splitlines():
                    xml_parts.append(f"\t\t{line}")
                xml_parts.append(f"\t</{file_tag}>")
            xml_parts.append(f"</{dir_tag}>")

        final_text = user_text + "\n" + "\n".join(xml_parts) + "\n"
        QGuiApplication.clipboard().setText(final_text)

    def clear_all(self):
        self.text_edit.clear()
        self.files_list.clear()
        self.attached_files.clear()
        self.attached_dirs.clear()
        self.load_template()

        # Aktualizacja licznika tokenów po wyczyszczeniu
        self.prompt_tokens = 0
        self.attachments_tokens = 0
        self.total_tokens = 0
        self.token_label.setText("Tokeny: prompt: 0 | pliki: 0 | suma: 0")
        self.token_label.setStyleSheet("")


def main():
    app = QApplication(sys.argv)
    window = PromptAssistant()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

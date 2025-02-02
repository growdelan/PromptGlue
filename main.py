import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, 
    QFileDialog, QListWidget, QListWidgetItem, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QGuiApplication


class PromptAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomocnik do tworzenia promptów")

        # Definicja domyślnego template
        self.template_text = """<Cel>

</Cel>

<Format_odpowiedzi>

<Format_odpowiedzi>

<Ostrzeżenia>

</Ostrzeżenia>

<Kontekst>

</Kontekst>
"""

        # Lista załączonych plików: przechowuje krotki (nazwa_pliku, zawartość)
        self.attached_files = []

        # Główny widget i layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Etykieta informacyjna
        label = QLabel("Wpisz treść promptu i załącz pliki, które chcesz do niego dodać:")
        layout.addWidget(label)

        # Duże pole tekstowe
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        # Załaduj domyślny template przy uruchomieniu aplikacji
        self.load_template()

        # Lista plików
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        # Kontener na przyciski
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Przycisk "Załącz pliki"
        self.attach_button = QPushButton("Załącz pliki")
        self.attach_button.clicked.connect(self.attach_files)
        button_layout.addWidget(self.attach_button)

        # Przycisk "Kopiuj"
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)

        # Przycisk "Clear"
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

    def load_template(self):
        """
        Ustawia domyślny template w głównym polu tekstowym.
        """
        self.text_edit.setPlainText(self.template_text)

    def attach_files(self):
        """
        Otwiera okno dialogowe, aby wybrać pliki do załączenia.
        Dodaje wybrane pliki do listy self.attached_files i wyświetla je w widoku self.files_list.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Wybierz pliki do załączenia",
            "",
            "Wszystkie pliki (*.*)"
        )

        for path in file_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    filename = os.path.basename(path)
                    self.attached_files.append((filename, content))
                    self.files_list.addItem(QListWidgetItem(filename))
                except Exception as e:
                    # Jeśli plik nie może być odczytany, można obsłużyć wyjątek lub wyświetlić komunikat
                    pass

    def copy_text(self):
        """
        Kopiuje do schowka tekst wprowadzony w polu 'self.text_edit'
        wraz z formatowaną zawartością załączonych plików.
        """
        user_text = self.text_edit.toPlainText()
        final_text = user_text + "\n<pliki>\n"

        for filename, content in self.attached_files:
            final_text += f"\t<{filename}>\n"
            # Dodatkowe wcięcie można dostosować wg preferencji
            # żeby zachować czytelność zawartości pliku
            for line in content.splitlines():
                final_text += f"\t\t{line}\n"
            final_text += f"\t</{filename}>\n"

        final_text += "</pliki>\n"

        # Kopiowanie do schowka
        QGuiApplication.clipboard().setText(final_text)

    def clear_all(self):
        """
        Czyści pole tekstowe oraz pamięć załączonych plików.
        Dzięki temu przycisk "Clear" usuwa nie tylko tekst z pola,
        ale również załączone pliki, umożliwiając ich ponowne dodanie.
        Po wyczyszczeniu, w pole tekstowe zostaje załadowany domyślny template.
        """
        self.text_edit.clear()
        self.files_list.clear()
        self.attached_files.clear()
        # Załaduj ponownie domyślny template
        self.load_template()


def main():
    app = QApplication(sys.argv)
    window = PromptAssistant()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

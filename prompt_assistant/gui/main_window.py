"""MainWindow: composes UI and hooks controllers."""
from __future__ import annotations

import sys
from PyQt5.QtWidgets import QApplication

from .controllers import (
    setup_ui,
    connect_signals,
    PromptAssistantWindow,
)

__all__ = ["main", "PromptAssistantWindow", "PromptAssistant"]

# Alias for consistency at package-level
PromptAssistant = PromptAssistantWindow

def main() -> None:
    app = QApplication(sys.argv)
    window = PromptAssistantWindow()
    setup_ui(window)
    connect_signals(window)
    window.show()
    sys.exit(app.exec_())

# for entry-point compatibility
if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()

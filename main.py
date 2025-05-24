"""Entry-point script for manual execution (python main.py)."""
from __future__ import annotations
import sys
from PyQt5.QtWidgets import QApplication
from prompt_assistant.gui.main_window import main

if __name__ == "__main__":
    main()
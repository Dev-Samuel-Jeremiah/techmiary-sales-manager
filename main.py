"""Techmiary Sales Manager — record services rendered and see daily and monthly takings.

Run:  python main.py
"""
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app import theme
from app.db import Database
from app.main_window import MainWindow
from app.widgets import logo_pixmap


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("Techmiary Sales Manager")
    app.setOrganizationName("Techmiary Technology Concepts")
    app.setStyle("Fusion")
    app.setStyleSheet(theme.build_style())
    app.setWindowIcon(QIcon(logo_pixmap(64)))

    db = Database()
    win = MainWindow(db)
    if db.is_empty():
        ans = QMessageBox.question(
            win, "Welcome to Techmiary Sales Manager",
            "Would you like to start with a sample list of common services (printing, typing, JAMB registration "
            "and more)?\n\nYou can change the prices or delete any of them later.")
        if ans == QMessageBox.Yes:
            db.seed_starter_services()
        win.go("tag")
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QFileDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                               QWidget)

from .db import Database
from .widgets import ICON_SIZE, Card, icon, label, page_header


class SettingsPage(QWidget):
    changed = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)
        head, _ = page_header("Settings", "Business details for receipts, and backups of your sales records.")
        lay.addLayout(head)

        row = QHBoxLayout()
        row.setSpacing(18)
        biz = Card("Business details")
        biz.lay.addWidget(label("These appear at the top of every receipt.", "Muted"))
        form = QFormLayout()
        form.setSpacing(10)
        self.fields = {}
        for key, text in [("business_name", "Business name"), ("business_address", "Address"),
                          ("business_phone", "Phone"), ("staff_name", "Cashier / staff name"), ("currency", "Currency symbol")]:
            e = QLineEdit()
            self.fields[key] = e
            form.addRow(text, e)
        self.fields["currency"].setMaxLength(4)
        self.fields["staff_name"].setPlaceholderText("Shown on receipts as 'Served by'")
        biz.lay.addLayout(form)
        save = QPushButton("  Save details")
        save.setObjectName("Primary")
        save.setIcon(icon("check", "#FFFFFF"))
        save.setIconSize(ICON_SIZE)
        save.clicked.connect(self.save)
        sr = QHBoxLayout()
        sr.addStretch(1)
        sr.addWidget(save)
        biz.lay.addLayout(sr)
        biz.lay.addStretch(1)
        row.addWidget(biz, 1)

        bk = Card("Backup & restore")
        bk.lay.addWidget(label("Your records are saved automatically on this computer. Make a backup to a flash drive "
                               "or Google Drive regularly, so you never lose your sales history.", "Muted", wrap=True))
        b1 = QPushButton("  Back up now")
        b1.setObjectName("Primary")
        b1.setIcon(icon("download", "#FFFFFF"))
        b1.setIconSize(ICON_SIZE)
        b1.clicked.connect(self.backup)
        b2 = QPushButton("  Restore from a backup")
        b2.setIcon(icon("upload"))
        b2.setIconSize(ICON_SIZE)
        b2.clicked.connect(self.restore)
        b3 = QPushButton("  Open data folder")
        b3.setIcon(icon("folder"))
        b3.setIconSize(ICON_SIZE)
        b3.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.db.path.parent))))
        for b in (b1, b2, b3):
            b.setMinimumHeight(40)
            bk.lay.addWidget(b)
        bk.lay.addWidget(label("Data file:", "Small"))
        self.path_lbl = label(str(db.path), "Small", wrap=True)
        bk.lay.addWidget(self.path_lbl)
        bk.lay.addStretch(1)
        row.addWidget(bk, 1)
        lay.addLayout(row)
        lay.addStretch(1)
        lay.addWidget(label("Techmiary Sales Manager · version 1.0 · built by Techmiary Technology Concepts", "Small"))

    def refresh(self):
        for k, e in self.fields.items():
            e.setText(self.db.setting(k))

    def save(self):
        if not self.fields["business_name"].text().strip():
            QMessageBox.warning(self, "Missing name", "Please enter the business name.")
            return
        for k, e in self.fields.items():
            self.db.set_setting(k, e.text().strip() or ("₦" if k == "currency" else ""))
        self.changed.emit()
        QMessageBox.information(self, "Saved", "Your business details have been saved.")

    def backup(self):
        name = f"TechmiarySales-backup-{datetime.now().strftime('%Y-%m-%d_%H%M')}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Save backup", str(Path.home() / name), "Backup (*.db)")
        if not path:
            return
        self.db.backup_to(Path(path))
        QMessageBox.information(self, "Backup complete", f"Backup saved to\n{path}")

    def restore(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose a backup", str(Path.home()), "Backup (*.db)")
        if not path:
            return
        if QMessageBox.question(self, "Restore backup",
                                "This replaces all current services and sales with the backup.\n"
                                "A copy of your current data is kept in the data folder first.\n\nContinue?") != QMessageBox.Yes:
            return
        try:
            self.db.restore_from(Path(path))
        except Exception as e:  # noqa: BLE001 - show any failure to the user
            QMessageBox.critical(self, "Restore failed", str(e))
            return
        self.refresh()
        self.changed.emit()
        QMessageBox.information(self, "Restored", "Your data has been restored from the backup.")

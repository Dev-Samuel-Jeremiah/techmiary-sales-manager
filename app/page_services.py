from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLineEdit,
                               QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget)

from . import theme
from .db import Database, Service
from .widgets import ICON_SIZE, Card, cell, icon, label, make_table, page_header

UNITS = ["per job", "per page", "per copy", "per sheet", "per set", "per hour", "per item", "per day", "per month"]


class ServiceDialog(QDialog):
    def __init__(self, db: Database, service: Service | None = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Edit service" if service else "Add a service")
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 22, 24, 20)
        lay.setSpacing(14)
        lay.addWidget(label("Edit service" if service else "Add a new service", "SectionTitle"))
        lay.addWidget(label("Services and their prices appear on the New sale screen.", "Muted"))

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.name = QLineEdit()
        self.name.setPlaceholderText("e.g. Printing (colour)")
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(db.categories() or ["General"])
        self.category.setCurrentText("")
        self.category.lineEdit().setPlaceholderText("e.g. Printing")
        self.price = QSpinBox()
        self.price.setRange(0, 100_000_000)
        self.price.setSingleStep(50)
        self.price.setPrefix(db.currency + " ")
        self.price.setGroupSeparatorShown(True)
        self.unit = QComboBox()
        self.unit.setEditable(True)
        self.unit.addItems(UNITS)
        self.desc = QPlainTextEdit()
        self.desc.setPlaceholderText("Optional note about this service")
        self.desc.setFixedHeight(70)
        self.active = QCheckBox("Available for sale")
        self.active.setChecked(True)
        form.addRow("Service name", self.name)
        form.addRow("Category", self.category)
        form.addRow("Price", self.price)
        form.addRow("Charged", self.unit)
        form.addRow("Description", self.desc)
        form.addRow("", self.active)
        lay.addLayout(form)

        if service:
            self.name.setText(service.name)
            self.category.setCurrentText(service.category)
            self.price.setValue(service.price)
            self.unit.setCurrentText(service.unit)
            self.desc.setPlainText(service.description)
            self.active.setChecked(service.active)

        btns = QDialogButtonBox()
        save = btns.addButton("Save service", QDialogButtonBox.AcceptRole)
        save.setObjectName("Primary")
        btns.addButton("Cancel", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Missing name", "Please enter the service name.")
            self.name.setFocus()
            return
        self.accept()

    def values(self) -> dict:
        return dict(name=self.name.text(), category=self.category.currentText() or "General", price=self.price.value(),
                    unit=self.unit.currentText(), description=self.desc.toPlainText(), active=self.active.isChecked())


class ServicesPage(QWidget):
    changed = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)
        head, _ = page_header("Services & prices", "Add the services you offer and what you charge for each.")
        add = QPushButton("  Add service")
        add.setObjectName("Primary")
        add.setIcon(icon("plus", "#FFFFFF"))
        add.setIconSize(ICON_SIZE)
        add.setMinimumHeight(42)
        add.clicked.connect(self.add)
        head.addWidget(add, 0, Qt.AlignTop)
        lay.addLayout(head)

        card = Card()
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search services…")
        self.search.addAction(icon("search", theme.MUTED), QLineEdit.LeadingPosition)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh)
        self.cat = QComboBox()
        self.cat.setMinimumWidth(200)
        self.cat.currentIndexChanged.connect(self.refresh)
        self.show_inactive = QCheckBox("Show unavailable")
        self.show_inactive.setChecked(True)
        self.show_inactive.toggled.connect(self.refresh)
        self.count = label("", "Muted")
        bar.addWidget(self.search, 2)
        bar.addWidget(self.cat, 1)
        bar.addWidget(self.show_inactive)
        bar.addStretch(1)
        bar.addWidget(self.count)
        card.lay.addLayout(bar)

        self.table = make_table(["Service", "Category", "Price", "Charged", "Status"], stretch_col=0)
        self.table.doubleClicked.connect(self.edit)
        self.table.itemSelectionChanged.connect(self._sel)
        card.lay.addWidget(self.table, 1)

        actions = QHBoxLayout()
        actions.addWidget(label("Tip: double-click a service to edit it.", "Small"))
        actions.addStretch(1)
        self.b_edit = QPushButton("  Edit")
        self.b_edit.setIcon(icon("edit", theme.INK))
        self.b_edit.clicked.connect(self.edit)
        self.b_del = QPushButton("  Delete")
        self.b_del.setObjectName("Danger")
        self.b_del.setIcon(icon("trash", theme.DANGER))
        self.b_del.clicked.connect(self.delete)
        actions.addWidget(self.b_edit)
        actions.addWidget(self.b_del)
        card.lay.addLayout(actions)
        lay.addWidget(card, 1)
        self._services: list[Service] = []

    def _sel(self):
        on = bool(self.table.selectedItems())
        self.b_edit.setEnabled(on)
        self.b_del.setEnabled(on)

    def refresh(self):
        cur = self.cat.currentText()
        self.cat.blockSignals(True)
        self.cat.clear()
        self.cat.addItem("All categories")
        self.cat.addItems(self.db.categories())
        idx = self.cat.findText(cur)
        self.cat.setCurrentIndex(max(0, idx))
        self.cat.blockSignals(False)
        category = "" if self.cat.currentIndex() <= 0 else self.cat.currentText()
        self._services = self.db.services(self.search.text().strip(), self.show_inactive.isChecked(), category)
        t = self.table
        t.setRowCount(len(self._services))
        for r, s in enumerate(self._services):
            t.setItem(r, 0, cell(s.name, bold=True, data=s.id))
            t.setItem(r, 1, cell(s.category, color=theme.MUTED))
            t.setItem(r, 2, cell(self.db.fmt(s.price), align_right=True, bold=True, color=theme.NAVY))
            t.setItem(r, 3, cell(s.unit, color=theme.MUTED))
            t.setItem(r, 4, cell("● Available" if s.active else "○ Unavailable",
                                 color=theme.TEAL_DARK if s.active else theme.MUTED))
        self.count.setText(f"{len(self._services)} service{'s' if len(self._services) != 1 else ''}")
        self._sel()

    def _current(self) -> Service | None:
        rows = self.table.selectionModel().selectedRows()
        return self._services[rows[0].row()] if rows else None

    def add(self):
        d = ServiceDialog(self.db, parent=self)
        if d.exec():
            self.db.add_service(**d.values())
            self.refresh()
            self.changed.emit()

    def edit(self):
        s = self._current()
        if not s:
            return
        d = ServiceDialog(self.db, s, parent=self)
        if d.exec():
            self.db.update_service(s.id, **d.values())
            self.refresh()
            self.changed.emit()

    def delete(self):
        s = self._current()
        if not s:
            return
        if QMessageBox.question(self, "Delete service", f"Delete “{s.name}”?") != QMessageBox.Yes:
            return
        deleted = self.db.delete_service(s.id)
        if not deleted:
            QMessageBox.information(self, "Marked unavailable",
                                    f"“{s.name}” already appears in past sales, so it was marked unavailable instead "
                                    "of deleted. Your sales records stay complete.")
        self.refresh()
        self.changed.emit()

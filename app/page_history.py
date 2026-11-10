from __future__ import annotations

import csv
from datetime import date, datetime, timedelta

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (QComboBox, QDateEdit, QFileDialog, QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                               QVBoxLayout, QWidget)

from . import theme
from .db import Database, month_bounds
from .receipt import ReceiptDialog
from .widgets import ICON_SIZE, Card, cell, icon, label, make_table, page_header

RANGES = ["Today", "Yesterday", "This week", "This month", "Last month", "This year", "Custom dates"]


def range_for(name: str, today: date | None = None) -> tuple[date, date]:
    t = today or date.today()
    if name == "Today":
        return t, t
    if name == "Yesterday":
        y = t - timedelta(days=1)
        return y, y
    if name == "This week":
        return t - timedelta(days=t.weekday()), t
    if name == "This month":
        return month_bounds(t)[0], t
    if name == "Last month":
        return month_bounds(month_bounds(t)[0] - timedelta(days=1))
    if name == "This year":
        return t.replace(month=1, day=1), t
    return t, t


class HistoryPage(QWidget):
    changed = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)
        head, _ = page_header("Sales history", "Every sale recorded, with receipts. Double-click a sale to view it.")
        exp = QPushButton("  Export CSV")
        exp.setIcon(icon("download"))
        exp.setIconSize(ICON_SIZE)
        exp.clicked.connect(self.export)
        head.addWidget(exp, 0, Qt.AlignTop)
        lay.addLayout(head)

        card = Card()
        bar = QHBoxLayout()
        bar.setSpacing(10)
        self.range = QComboBox()
        self.range.addItems(RANGES)
        self.range.setCurrentText("Today")
        self.range.currentIndexChanged.connect(self._range_changed)
        self.d_from = QDateEdit(QDate.currentDate())
        self.d_to = QDateEdit(QDate.currentDate())
        for d in (self.d_from, self.d_to):
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd MMM yyyy")
            d.dateChanged.connect(self._dates_edited)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search customer, phone, receipt or service…")
        self.search.addAction(icon("search", theme.MUTED), QLineEdit.LeadingPosition)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh)
        self.pay = QComboBox()
        self.pay.addItems(["All payments", "Cash", "Transfer", "POS"])
        self.pay.currentIndexChanged.connect(self.refresh)
        bar.addWidget(self.range)
        bar.addWidget(self.d_from)
        bar.addWidget(label("to", "Muted"))
        bar.addWidget(self.d_to)
        bar.addWidget(self.search, 1)
        bar.addWidget(self.pay)
        card.lay.addLayout(bar)

        self.table = make_table(["Date & time", "Receipt", "Customer", "Services", "Payment", "Discount", "Amount"], stretch_col=3)
        self.table.doubleClicked.connect(self.view)
        self.table.itemSelectionChanged.connect(self._sel)
        card.lay.addWidget(self.table, 1)

        foot = QHBoxLayout()
        self.summary = label("", "")
        self.summary.setStyleSheet(f"font-size: 14px; color: {theme.NAVY};")
        foot.addWidget(self.summary)
        foot.addStretch(1)
        self.b_view = QPushButton("  View receipt")
        self.b_view.setIcon(icon("receipt"))
        self.b_view.clicked.connect(self.view)
        self.b_void = QPushButton("  Void sale")
        self.b_void.setObjectName("Danger")
        self.b_void.setIcon(icon("x", theme.DANGER))
        self.b_void.clicked.connect(self.toggle_void)
        foot.addWidget(self.b_view)
        foot.addWidget(self.b_void)
        card.lay.addLayout(foot)
        lay.addWidget(card, 1)
        self._rows = []
        self._busy = False

    def _range_changed(self):
        name = self.range.currentText()
        if name != "Custom dates":
            a, b = range_for(name)
            self._busy = True
            self.d_from.setDate(QDate(a.year, a.month, a.day))
            self.d_to.setDate(QDate(b.year, b.month, b.day))
            self._busy = False
        self.refresh()

    def _dates_edited(self):
        if self._busy:
            return
        self.range.blockSignals(True)
        self.range.setCurrentText("Custom dates")
        self.range.blockSignals(False)
        self.refresh()

    def show_range(self, name: str):
        self.range.setCurrentText(name)
        self._range_changed()

    def _sel(self):
        rows = self.table.selectionModel().selectedRows()
        self.b_view.setEnabled(bool(rows))
        self.b_void.setEnabled(bool(rows))
        if rows:
            voided = self._rows[rows[0].row()]["voided"]
            self.b_void.setText("  Restore sale" if voided else "  Void sale")
            self.b_void.setIcon(icon("undo", theme.DANGER) if voided else icon("x", theme.DANGER))

    def refresh(self):
        if self.range.currentText() != "Custom dates":
            a, b = range_for(self.range.currentText())
            self._busy = True
            self.d_from.setDate(QDate(a.year, a.month, a.day))
            self.d_to.setDate(QDate(b.year, b.month, b.day))
            self._busy = False
        a, b = self.d_from.date().toPython(), self.d_to.date().toPython()
        if b < a:
            a, b = b, a
        pay = "" if self.pay.currentIndex() == 0 else self.pay.currentText()
        self._rows = self.db.sales_between(a, b, self.search.text().strip(), True, pay)
        t = self.table
        t.setRowCount(len(self._rows))
        total = count = 0
        for r, s in enumerate(self._rows):
            v = bool(s["voided"])
            when = datetime.strptime(s["created_at"], "%Y-%m-%d %H:%M:%S")
            grey = theme.MUTED if v else None
            t.setItem(r, 0, cell(when.strftime("%d %b %Y, %I:%M %p"), color=theme.MUTED))
            t.setItem(r, 1, cell(s["receipt_no"] + ("  (void)" if v else ""), color=theme.DANGER if v else None))
            t.setItem(r, 2, cell(s["customer_name"] or "Walk-in customer", color=grey))
            t.setItem(r, 3, cell(s["summary"] or "", color=grey))
            t.setItem(r, 4, cell(s["payment_method"], color=grey))
            t.setItem(r, 5, cell(self.db.fmt(s["discount"]) if s["discount"] else "—", align_right=True, color=theme.MUTED))
            t.setItem(r, 6, cell(self.db.fmt(s["total"]), align_right=True, bold=not v,
                                 color=theme.MUTED if v else theme.NAVY))
            if not v:
                total += s["total"]
                count += 1
        span = a.strftime("%d %b %Y") if a == b else f"{a.strftime('%d %b')} – {b.strftime('%d %b %Y')}"
        self.summary.setText(f"<b>{self.db.fmt(total)}</b> from {count} sale{'s' if count != 1 else ''} · {span}")
        self._sel()

    def _current(self):
        rows = self.table.selectionModel().selectedRows()
        return self._rows[rows[0].row()] if rows else None

    def view(self):
        s = self._current()
        if s:
            ReceiptDialog(self.db, s["id"], self, title=f"Receipt {s['receipt_no']}").exec()

    def toggle_void(self):
        s = self._current()
        if not s:
            return
        if s["voided"]:
            self.db.void_sale(s["id"], False)
        else:
            if QMessageBox.question(self, "Void sale",
                                    f"Void sale {s['receipt_no']} ({self.db.fmt(s['total'])})?\n\n"
                                    "It stays in the history but no longer counts in your totals.") != QMessageBox.Yes:
                return
            self.db.void_sale(s["id"], True)
        self.refresh()
        self.changed.emit()

    def export(self):
        a, b = self.d_from.date().toPython(), self.d_to.date().toPython()
        path, _ = QFileDialog.getSaveFileName(self, "Export sales", f"Sales {a} to {b}.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Time", "Receipt", "Customer", "Phone", "Services", "Payment", "Discount", "Amount", "Status", "Note"])
            for s in self._rows:
                d, tm = s["created_at"].split(" ")
                w.writerow([d, tm[:5], s["receipt_no"], s["customer_name"], s["customer_phone"], s["summary"],
                            s["payment_method"], s["discount"], s["total"], "Void" if s["voided"] else "OK", s["note"]])
        QMessageBox.information(self, "Exported", f"Saved {len(self._rows)} sales to\n{path}\n\nYou can open it in Excel.")

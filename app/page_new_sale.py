from __future__ import annotations

from PySide6.QtCore import QDateTime, Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QDateTimeEdit, QDialog, QDialogButtonBox, QFormLayout, QFrame, QGridLayout,
                               QHBoxLayout, QHeaderView, QLineEdit, QMessageBox, QPushButton, QScrollArea, QSpinBox,
                               QToolButton, QVBoxLayout, QWidget)

from . import theme
from .db import Database, Service
from .receipt import ReceiptDialog
from .widgets import FlowLayout, ICON_SIZE, Card, cell, empty_state, icon, label, make_table, page_header

PAYMENTS = ["Cash", "Transfer", "POS"]


class ServiceTile(QFrame):
    clicked = Signal(object)

    def __init__(self, s: Service, db: Database):
        super().__init__()
        self.s = s
        self.setObjectName("Tile")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(86)
        self.setStyleSheet(f"""
            QFrame#Tile {{ background: white; border: 1px solid {theme.LINE}; border-radius: 12px; }}
            QFrame#Tile:hover {{ border: 1.5px solid {theme.BLUE}; background: #FAFCFF; }}""")
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(3)
        cat = label(s.category.upper(), "Small")
        cat.setStyleSheet(f"color: {theme.TEAL_DARK}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        name = label(s.name, wrap=True)
        name.setStyleSheet("font-weight: 700; font-size: 13.5px;")
        price = label(f"{db.fmt(s.price)}  <span style='color:{theme.MUTED};font-weight:400;font-size:11px'>{s.unit}</span>")
        price.setStyleSheet(f"color: {theme.BLUE}; font-weight: 800; font-size: 14px;")
        for w in (cat, name, price):
            w.setAttribute(Qt.WA_TransparentForMouseEvents)
            v.addWidget(w)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.s)


class CustomItemDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a custom item")
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.addWidget(label("Custom item", "SectionTitle"))
        lay.addWidget(label("For a one-off job that is not in your services list.", "Muted"))
        f = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("What did you do for the customer?")
        self.price = QSpinBox()
        self.price.setRange(0, 100_000_000)
        self.price.setSingleStep(50)
        self.price.setPrefix(db.currency + " ")
        self.price.setGroupSeparatorShown(True)
        f.addRow("Description", self.name)
        f.addRow("Price", self.price)
        lay.addLayout(f)
        b = QDialogButtonBox()
        ok = b.addButton("Add to sale", QDialogButtonBox.AcceptRole)
        ok.setObjectName("Primary")
        b.addButton("Cancel", QDialogButtonBox.RejectRole)
        b.accepted.connect(lambda: self.accept() if self.name.text().strip() else self.name.setFocus())
        b.rejected.connect(self.reject)
        lay.addWidget(b)


class NewSalePage(QWidget):
    sale_recorded = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        self.items: list[dict] = []
        self.active_cat = ""

        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)
        head, _ = page_header("New sale", "Tap a service to add it, then complete the sale.")
        lay.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(18)
        lay.addLayout(body, 1)

        # ---------- catalog ----------
        cat_card = Card()
        sr = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search services…")
        self.search.addAction(icon("search", theme.MUTED), QLineEdit.LeadingPosition)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.build_catalog)
        self.search.returnPressed.connect(self._add_first)
        custom = QPushButton("  Custom item")
        custom.setIcon(icon("plus"))
        custom.setIconSize(ICON_SIZE)
        custom.clicked.connect(self.add_custom)
        sr.addWidget(self.search, 1)
        sr.addWidget(custom)
        cat_card.lay.addLayout(sr)
        chips_w = QWidget()
        self.chips_row = FlowLayout(chips_w, spacing=8)
        cat_card.lay.addWidget(chips_w)
        self.chip_group = QButtonGroup(self)
        self.chip_group.setExclusive(True)

        self.grid_host = QWidget()
        self.grid_host.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 6, 0)
        self.grid.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.grid_host)
        scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        cat_card.lay.addWidget(scroll, 1)
        body.addWidget(cat_card, 3)

        # ---------- cart ----------
        cart = Card("Current sale")
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        cart.header.addWidget(self.clear_btn)
        self.table = make_table(["Service", "Price", "Qty", "Amount", ""], stretch_col=0)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 76)
        self.table.setColumnWidth(4, 44)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setSelectionMode(self.table.SelectionMode.NoSelection)
        self.table.setStyleSheet("QTableWidget::item { padding: 0 6px; }")
        self.table.setMinimumHeight(180)
        cart.lay.addWidget(self.table, 1)
        self.empty_hint = empty_state("No services added yet.\nClick a service on the left to add it.")
        cart.lay.addWidget(self.empty_hint)

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.cust_name = QLineEdit()
        self.cust_name.setPlaceholderText("Customer name (optional)")
        self.cust_phone = QLineEdit()
        self.cust_phone.setPlaceholderText("Phone (optional)")
        form.addWidget(self.cust_name, 0, 0)
        form.addWidget(self.cust_phone, 0, 1)
        pay_row = QHBoxLayout()
        pay_row.setSpacing(8)
        self.pay_group = QButtonGroup(self)
        for i, p in enumerate(PAYMENTS):
            b = QPushButton(p)
            b.setObjectName("Seg")
            b.setCheckable(True)
            b.setChecked(i == 0)
            self.pay_group.addButton(b, i)
            pay_row.addWidget(b)
        pw = QWidget()
        pw.setLayout(pay_row)
        pay_row.setContentsMargins(0, 0, 0, 0)
        form.addWidget(label("Payment", "StatLabel"), 1, 0, 1, 2)
        form.addWidget(pw, 2, 0, 1, 2)
        self.discount = QSpinBox()
        self.discount.setRange(0, 100_000_000)
        self.discount.setSingleStep(50)
        self.discount.setPrefix("Discount  " + db.currency + " ")
        self.discount.setGroupSeparatorShown(True)
        self.discount.valueChanged.connect(self.update_totals)
        self._when_edited = False
        self.when = QDateTimeEdit(QDateTime.currentDateTime())
        self.when.dateTimeChanged.connect(self._on_when_changed)
        self.when.setDisplayFormat("dd MMM yyyy, hh:mm AP")
        self.when.setCalendarPopup(True)
        self.when.setToolTip("Change this only when entering an older sale from paper records.")
        form.addWidget(self.discount, 3, 0)
        form.addWidget(self.when, 3, 1)
        self.note = QLineEdit()
        self.note.setPlaceholderText("Note (optional)")
        form.addWidget(self.note, 4, 0, 1, 2)
        cart.lay.addLayout(form)

        total = QFrame()
        total.setObjectName("TotalPanel")
        tl = QHBoxLayout(total)
        tl.setContentsMargins(20, 14, 20, 14)
        tc = QVBoxLayout()
        tc.setSpacing(0)
        tc.addWidget(label("TOTAL TO PAY", "TotalLabel"))
        self.total_lbl = label(db.fmt(0), "TotalValue")
        tc.addWidget(self.total_lbl)
        self.sub_lbl = label("", "TotalSmall")
        tc.addWidget(self.sub_lbl)
        tl.addLayout(tc, 1)
        cart.lay.addWidget(total)

        self.complete = QPushButton("  Complete sale")
        self.complete.setObjectName("Success")
        self.complete.setIcon(icon("check", "#FFFFFF"))
        self.complete.setIconSize(ICON_SIZE)
        self.complete.setMinimumHeight(50)
        self.complete.clicked.connect(self.complete_sale)
        cart.lay.addWidget(self.complete)
        cart.setMinimumWidth(470)
        body.addWidget(cart, 2)

        self.update_totals()

    # ---------- catalog ----------
    def refresh(self):
        self.currency_refresh()
        # rebuild chips
        while self.chips_row.count():
            it = self.chips_row.takeAt(0)
            if it.widget():
                self.chip_group.removeButton(it.widget())
                it.widget().deleteLater()
        cats = [""] + [c for c in self.db.categories()
                       if any(s.category == c for s in self.db.services(include_inactive=False))]
        if self.active_cat not in cats:
            self.active_cat = ""
        for c in cats:
            b = QPushButton(c or "All")
            b.setObjectName("Chip")
            b.setCheckable(True)
            b.setChecked(c == self.active_cat)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, c=c: self._pick_cat(c))
            self.chip_group.addButton(b)
            self.chips_row.addWidget(b)
        self.build_catalog()
        if not self.items:
            self._reset_when()

    def currency_refresh(self):
        self.discount.setPrefix("Discount  " + self.db.currency + " ")
        self.update_totals()

    def _pick_cat(self, c: str):
        self.active_cat = c
        self.build_catalog()

    def _visible_services(self) -> list[Service]:
        return self.db.services(self.search.text().strip(), include_inactive=False, category=self.active_cat)

    def build_catalog(self):
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        services = self._visible_services()
        cols = 3
        for i, s in enumerate(services):
            t = ServiceTile(s, self.db)
            t.clicked.connect(self.add_service)
            self.grid.addWidget(t, i // cols, i % cols)
        if not services:
            self.grid.addWidget(empty_state("No services found. Add services on the Services & prices page."), 0, 0, 1, cols)
        for c in range(cols):
            self.grid.setColumnStretch(c, 1)
        self.grid.setRowStretch(len(services) // cols + 1, 1)

    def _add_first(self):
        s = self._visible_services()
        if s:
            self.add_service(s[0])
            self.search.selectAll()

    # ---------- cart ----------
    def add_service(self, s: Service):
        for it in self.items:
            if it["service_id"] == s.id and it["unit_price"] == s.price:
                it["quantity"] += 1
                self.render_cart()
                return
        self.items.append(dict(service_id=s.id, service_name=s.name, category=s.category, unit_price=s.price, quantity=1))
        self.render_cart()

    def add_custom(self):
        d = CustomItemDialog(self.db, self)
        if d.exec():
            self.items.append(dict(service_id=None, service_name=d.name.text().strip(), category="Other",
                                   unit_price=d.price.value(), quantity=1))
            self.render_cart()

    def render_cart(self):
        t = self.table
        t.setRowCount(0)
        t.setRowCount(len(self.items))
        for r, it in enumerate(self.items):
            t.setItem(r, 0, cell(it["service_name"], bold=True))
            price = QSpinBox()
            price.setRange(0, 100_000_000)
            price.setSingleStep(50)
            price.setGroupSeparatorShown(True)
            price.setValue(it["unit_price"])
            price.setPrefix(self.db.currency)
            price.setStyleSheet("padding: 3px 8px;")
            price.valueChanged.connect(lambda v, it=it: self._set(it, "unit_price", v))
            t.setCellWidget(r, 1, self._wrap(price))
            qty = QSpinBox()
            qty.setRange(1, 100000)
            qty.setValue(it["quantity"])
            qty.setStyleSheet("padding: 3px 4px;")
            qty.valueChanged.connect(lambda v, it=it: self._set(it, "quantity", v))
            t.setCellWidget(r, 2, self._wrap(qty))
            t.setItem(r, 3, cell(self.db.fmt(it["unit_price"] * it["quantity"]), align_right=True, bold=True, color=theme.NAVY))
            rm = QToolButton()
            rm.setIcon(icon("x", theme.DANGER, 16))
            rm.setToolTip("Remove")
            rm.setStyleSheet("QToolButton { border: none; border-radius: 6px; padding: 6px; } QToolButton:hover { background: #FDECEC; }")
            rm.clicked.connect(lambda _=False, it=it: self._remove(it))
            t.setCellWidget(r, 4, rm)
        self.empty_hint.setVisible(not self.items)
        self.update_totals()

    @staticmethod
    def _wrap(w):
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        h = QHBoxLayout(box)
        h.setContentsMargins(3, 6, 3, 6)
        h.addWidget(w)
        return box

    def _set(self, it, key, v):
        it[key] = v
        r = self.items.index(it)
        self.table.setItem(r, 3, cell(self.db.fmt(it["unit_price"] * it["quantity"]), align_right=True, bold=True, color=theme.NAVY))
        self.update_totals()

    def _remove(self, it):
        self.items.remove(it)
        self.render_cart()

    def subtotal(self) -> int:
        return sum(i["unit_price"] * i["quantity"] for i in self.items)

    def update_totals(self):
        sub = self.subtotal()
        disc = min(self.discount.value(), sub)
        self.total_lbl.setText(self.db.fmt(sub - disc))
        n = sum(i["quantity"] for i in self.items)
        extra = f" · discount {self.db.fmt(disc)}" if disc else ""
        self.sub_lbl.setText(f"{n} item{'s' if n != 1 else ''} · subtotal {self.db.fmt(sub)}{extra}")
        self.complete.setEnabled(bool(self.items))
        self.clear_btn.setEnabled(bool(self.items))

    def clear(self):
        self.items.clear()
        self.cust_name.clear()
        self.cust_phone.clear()
        self.note.clear()
        self.discount.setValue(0)
        self.pay_group.button(0).setChecked(True)
        self._reset_when()
        self.render_cart()

    def _reset_when(self):
        self.when.blockSignals(True)
        self.when.setDateTime(QDateTime.currentDateTime())
        self.when.blockSignals(False)
        self._when_edited = False

    def _on_when_changed(self, _):
        self._when_edited = True

    def complete_sale(self):
        if not self.items:
            return
        if self.discount.value() > self.subtotal():
            QMessageBox.warning(self, "Discount too large", "The discount cannot be more than the subtotal.")
            return
        # If the cashier did not change the date/time, stamp the sale with the real current time.
        from datetime import datetime
        when = self.when.dateTime().toPython() if self._when_edited else datetime.now()
        sale_id, receipt = self.db.record_sale(
            self.items, self.cust_name.text(), self.cust_phone.text(), PAYMENTS[self.pay_group.checkedId()],
            self.discount.value(), self.note.text(), when)
        self.clear()
        self.sale_recorded.emit()
        ReceiptDialog(self.db, sale_id, self, title=f"Sale recorded · {receipt}").exec()

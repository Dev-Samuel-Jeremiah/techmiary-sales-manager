from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout,
                               QWidget)

from . import theme
from .db import Database
from .page_dashboard import DashboardPage
from .page_history import HistoryPage
from .page_new_sale import NewSalePage
from .page_reports import ReportsPage
from .page_services import ServicesPage
from .page_settings import SettingsPage
from .widgets import icon, label, logo_pixmap

NAV = [("dashboard", "Dashboard", "Ctrl+1"), ("cart", "New sale", "Ctrl+N"), ("list", "Sales history", "Ctrl+3"),
       ("tag", "Services && prices", "Ctrl+4"), ("chart", "Reports", "Ctrl+5"), ("settings", "Settings", "Ctrl+6")]


class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Techmiary Sales Manager")
        self.resize(1360, 860)
        self.setMinimumSize(1120, 700)

        root = QWidget()
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        self.setCentralWidget(root)

        side = QWidget()
        side.setObjectName("Sidebar")
        side.setFixedWidth(240)
        sv = QVBoxLayout(side)
        sv.setContentsMargins(16, 22, 16, 18)
        sv.setSpacing(6)
        brand = QHBoxLayout()
        brand.setSpacing(10)
        lg = QLabel()
        lg.setPixmap(logo_pixmap(38))
        brand.addWidget(lg)
        bt = QVBoxLayout()
        bt.setSpacing(0)
        bt.addWidget(label("Techmiary", "BrandName"))
        bt.addWidget(label("SALES MANAGER", "BrandSub"))
        brand.addLayout(bt)
        brand.addStretch(1)
        sv.addLayout(brand)
        sv.addSpacing(26)

        self.stack = QStackedWidget()
        self.pages = {
            "dashboard": DashboardPage(db), "cart": NewSalePage(db), "list": HistoryPage(db),
            "tag": ServicesPage(db), "chart": ReportsPage(db), "settings": SettingsPage(db)}
        self.group = QButtonGroup(self)
        self.buttons = {}
        for i, (key, text, sc) in enumerate(NAV):
            b = QPushButton("   " + text)
            b.setObjectName("NavButton")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setIcon(icon(key, "#C9D4E5", 20))
            b.setIconSize(QSize(20, 20))
            b.setToolTip(f"{text.replace('&&', '&')}  ({sc})")
            b.clicked.connect(lambda _=False, k=key: self.go(k))
            self.group.addButton(b, i)
            self.buttons[key] = b
            sv.addWidget(b)
            self.stack.addWidget(self.pages[key])
            QShortcut(QKeySequence(sc), self, activated=lambda k=key: self.go(k))
            if key == "list":
                sv.addSpacing(0)
        sv.addStretch(1)
        self.foot_biz = label("", "SideFoot", wrap=True)
        sv.addWidget(self.foot_biz)
        h.addWidget(side)
        h.addWidget(self.stack, 1)

        p = self.pages
        p["dashboard"].new_sale_requested.connect(lambda: self.go("cart"))
        p["dashboard"].open_history.connect(lambda: (self.go("list"), p["list"].show_range("This month")))
        for k in ("cart", "list", "tag", "settings"):
            sig = getattr(p[k], "sale_recorded", None) or getattr(p[k], "changed", None)
            sig.connect(self._data_changed)
        self.go("dashboard")
        # Keep "today" figures correct if the app stays open past midnight.
        self._timer = QTimer(self, interval=60_000, timeout=self._tick)
        self._timer.start()

    def go(self, key: str):
        for k, b in self.buttons.items():
            b.setChecked(k == key)
            b.setIcon(icon(k, "#FFFFFF" if k == key else "#C9D4E5", 20))
        page = self.pages[key]
        self.stack.setCurrentWidget(page)
        page.refresh()
        self.foot_biz.setText(f"{self.db.setting('business_name')}\n{self.db.setting('business_address')}")

    def _data_changed(self):
        self.foot_biz.setText(f"{self.db.setting('business_name')}\n{self.db.setting('business_address')}")

    def _tick(self):
        if self.stack.currentWidget() is self.pages["dashboard"]:
            self.pages["dashboard"].refresh()

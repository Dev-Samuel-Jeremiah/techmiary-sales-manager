from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from . import theme
from .db import Database, month_bounds
from .widgets import (ICON_SIZE, BarChart, Card, StatCard, cell, empty_state, icon, label, make_table, page_header)


class DashboardPage(QWidget):
    new_sale_requested = Signal()
    open_history = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        body = QWidget()
        body.setObjectName("Page")
        scroll.setWidget(body)
        lay = QVBoxLayout(body)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(20)

        head, col = page_header("Dashboard", "")
        self.subtitle = col.itemAt(0).widget()
        self.greeting = label("", "PageSub")
        col.addWidget(self.greeting)
        btn = QPushButton("  New sale")
        btn.setObjectName("Primary")
        btn.setIcon(icon("plus", "#FFFFFF"))
        btn.setIconSize(ICON_SIZE)
        btn.setMinimumHeight(42)
        btn.clicked.connect(self.new_sale_requested)
        head.addWidget(btn, 0, Qt.AlignTop)
        lay.addLayout(head)

        grid = QGridLayout()
        grid.setSpacing(16)
        self.c_today = StatCard("Today's sales", "wallet", theme.BLUE, theme.BLUE_SOFT)
        self.c_count = StatCard("Customers served today", "users", theme.TEAL_DARK, theme.TEAL_SOFT)
        self.c_month = StatCard("This month", "calendar", theme.NAVY, "#E6EBF2")
        self.c_avg = StatCard("Daily average (month)", "trend", theme.AMBER, "#FDF3DE")
        for i, c in enumerate((self.c_today, self.c_count, self.c_month, self.c_avg)):
            grid.addWidget(c, 0, i)
        lay.addLayout(grid)

        row = QHBoxLayout()
        row.setSpacing(16)
        chart_card = Card("Sales — last 30 days")
        self.chart_total = label("", "Muted")
        chart_card.header.addWidget(self.chart_total)
        self.chart = BarChart()
        self.chart.setMinimumHeight(260)
        chart_card.lay.addWidget(self.chart)
        row.addWidget(chart_card, 3)

        top_card = Card("Top services this month")
        self.top_box = QVBoxLayout()
        self.top_box.setSpacing(10)
        top_card.lay.addLayout(self.top_box)
        top_card.lay.addStretch(1)
        row.addWidget(top_card, 2)
        lay.addLayout(row)

        recent = Card("Recent sales")
        see_all = QPushButton("See all")
        see_all.clicked.connect(self.open_history)
        recent.header.addWidget(see_all)
        self.table = make_table(["Time", "Receipt", "Customer", "Services", "Payment", "Amount"], stretch_col=3)
        self.table.setMinimumHeight(330)
        recent.lay.addWidget(self.table)
        lay.addWidget(recent)
        lay.addStretch(1)

    def refresh(self):
        db = self.db
        today = date.today()
        hour = datetime.now().hour
        part = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        staff = db.setting("staff_name")
        self.greeting.setText(f"Good {part}{', ' + staff if staff else ''} — {today.strftime('%A, %d %B %Y')}")

        t_total, t_count = db.total_between(today, today)
        y = today - timedelta(days=1)
        y_total, _ = db.total_between(y, y)
        diff = t_total - y_total
        hint = "Same as yesterday" if diff == 0 else f"{'▲' if diff > 0 else '▼'} {db.fmt(abs(diff))} vs yesterday"
        self.c_today.set(db.fmt(t_total), hint)
        self.c_count.set(f"{t_count:,}", "sales recorded today")

        m_start, m_end = month_bounds(today)
        m_total, m_count = db.total_between(m_start, m_end)
        self.c_month.set(db.fmt(m_total), f"{m_count:,} sales in {today.strftime('%B')}")
        days = today.day
        self.c_avg.set(db.fmt(round(m_total / days)), f"over {days} day{'s' if days > 1 else ''}")

        start = today - timedelta(days=29)
        series = db.daily_totals(start, today)
        self.chart.fmt = db.fmt
        self.chart.set_data([(d.strftime("%d %b"), v, f"{d.strftime('%a %d %b')}\n{db.fmt(v)} · {c} sale{'s' if c != 1 else ''}")
                             for d, v, c in series], highlight_index=len(series) - 1, label_every=5)
        self.chart_total.setText(f"Total {db.fmt(sum(v for _, v, _ in series))}")

        while self.top_box.count():
            it = self.top_box.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        top = db.service_breakdown(m_start, m_end)[:6]
        if not top:
            self.top_box.addWidget(empty_state("No sales this month yet"))
        best = top[0][3] if top else 1
        for name, cat, qty, rev in top:
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(5)
            h = QHBoxLayout()
            n = label(name)
            n.setStyleSheet("font-weight: 600;")
            h.addWidget(n, 1)
            amt = label(db.fmt(rev))
            amt.setStyleSheet(f"font-weight: 700; color: {theme.NAVY};")
            h.addWidget(amt)
            v.addLayout(h)
            bar_bg = QWidget()
            bar_bg.setFixedHeight(6)
            bar_bg.setStyleSheet(f"background: #EEF2F7; border-radius: 3px;")
            bar = QWidget(bar_bg)
            bar.setStyleSheet(f"background: {theme.TEAL}; border-radius: 3px;")
            bar.setFixedHeight(6)
            bar_bg.resizeEvent = lambda e, b=bar, frac=rev / best: b.setFixedWidth(max(6, int(e.size().width() * frac)))
            v.addWidget(bar_bg)
            v.addWidget(label(f"{cat} · {qty:,} sold", "Small"))
            self.top_box.addWidget(w)

        rows = db.sales_between(today - timedelta(days=60), today, include_voided=False)[:10]
        self.table.setRowCount(len(rows))
        for r, s in enumerate(rows):
            when = datetime.strptime(s["created_at"], "%Y-%m-%d %H:%M:%S")
            stamp = when.strftime("%I:%M %p") if when.date() == today else when.strftime("%d %b, %I:%M %p")
            self.table.setItem(r, 0, cell(stamp, color=theme.MUTED))
            self.table.setItem(r, 1, cell(s["receipt_no"]))
            self.table.setItem(r, 2, cell(s["customer_name"] or "Walk-in customer"))
            self.table.setItem(r, 3, cell(s["summary"] or ""))
            self.table.setItem(r, 4, cell(s["payment_method"]))
            self.table.setItem(r, 5, cell(db.fmt(s["total"]), align_right=True, bold=True, color=theme.NAVY))

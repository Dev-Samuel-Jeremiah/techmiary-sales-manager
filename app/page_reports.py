from __future__ import annotations

import calendar
import csv
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QComboBox, QDateEdit, QFileDialog, QGridLayout, QHBoxLayout, QMessageBox, QPushButton,
                               QScrollArea, QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from . import theme
from .db import Database, month_bounds
from .widgets import ICON_SIZE, BarChart, Card, StatCard, cell, icon, label, make_table, page_header


def _scroll_body():
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    body = QWidget()
    body.setObjectName("Page")
    scroll.setWidget(body)
    lay = QVBoxLayout(body)
    lay.setContentsMargins(0, 16, 8, 8)
    lay.setSpacing(16)
    return scroll, lay


def _stats_row(lay, cards):
    g = QGridLayout()
    g.setSpacing(16)
    for i, c in enumerate(cards):
        g.addWidget(c, 0, i)
    lay.addLayout(g)


def _fill_services(db, table, rows):
    table.setRowCount(len(rows))
    total = sum(r[3] for r in rows) or 1
    for i, (name, cat, qty, rev) in enumerate(rows):
        table.setItem(i, 0, cell(name, bold=True))
        table.setItem(i, 1, cell(cat, color=theme.MUTED))
        table.setItem(i, 2, cell(f"{qty:,}", align_right=True))
        table.setItem(i, 3, cell(db.fmt(rev), align_right=True, bold=True, color=theme.NAVY))
        table.setItem(i, 4, cell(f"{rev * 100 / total:.0f}%", align_right=True, color=theme.MUTED))
    table.setMinimumHeight(60 + 40 * max(len(rows), 3))


def _fill_payments(db, table, rows):
    table.setRowCount(len(rows))
    for i, (m, tot, n) in enumerate(rows):
        table.setItem(i, 0, cell(m, bold=True))
        table.setItem(i, 1, cell(f"{n:,}", align_right=True))
        table.setItem(i, 2, cell(db.fmt(tot), align_right=True, bold=True, color=theme.NAVY))
    table.setMinimumHeight(60 + 40 * max(len(rows), 3))


class ReportsPage(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setObjectName("Page")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 20)
        lay.setSpacing(10)
        head, _ = page_header("Reports", "How much the shop made — by day, month and year.")
        exp = QPushButton("  Export report")
        exp.setIcon(icon("download"))
        exp.setIconSize(ICON_SIZE)
        exp.clicked.connect(self.export)
        head.addWidget(exp, 0, Qt.AlignTop)
        lay.addLayout(head)
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.refresh)
        lay.addWidget(self.tabs, 1)
        self._build_daily()
        self._build_monthly()
        self._build_yearly()

    # ---------- daily ----------
    def _build_daily(self):
        scroll, lay = _scroll_body()
        bar = QHBoxLayout()
        bar.addWidget(label("Day:", "Muted"))
        self.day = QDateEdit(QDate.currentDate())
        self.day.setCalendarPopup(True)
        self.day.setDisplayFormat("dddd, dd MMMM yyyy")
        self.day.setMinimumWidth(240)
        self.day.dateChanged.connect(self.refresh)
        prev_b, next_b, today_b = QPushButton("‹ Previous"), QPushButton("Next ›"), QPushButton("Today")
        prev_b.clicked.connect(lambda: self.day.setDate(self.day.date().addDays(-1)))
        next_b.clicked.connect(lambda: self.day.setDate(self.day.date().addDays(1)))
        today_b.clicked.connect(lambda: self.day.setDate(QDate.currentDate()))
        for w in (self.day, prev_b, next_b, today_b):
            bar.addWidget(w)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.d_total = StatCard("Made this day", "wallet", theme.BLUE, theme.BLUE_SOFT)
        self.d_count = StatCard("Sales", "receipt", theme.TEAL_DARK, theme.TEAL_SOFT)
        self.d_avg = StatCard("Average sale", "trend", theme.AMBER, "#FDF3DE")
        self.d_disc = StatCard("Discounts given", "tag", theme.DANGER, theme.DANGER_SOFT)
        _stats_row(lay, [self.d_total, self.d_count, self.d_avg, self.d_disc])
        row = QHBoxLayout()
        row.setSpacing(16)
        c1 = Card("By service")
        self.d_services = make_table(["Service", "Category", "Qty", "Amount", "Share"], 0)
        c1.lay.addWidget(self.d_services)
        c2 = Card("By payment method")
        self.d_pay = make_table(["Method", "Sales", "Amount"], 0)
        c2.lay.addWidget(self.d_pay)
        c2.lay.addStretch(1)
        row.addWidget(c1, 3)
        row.addWidget(c2, 2)
        lay.addLayout(row)
        lay.addStretch(1)
        self.tabs.addTab(scroll, "Daily")

    # ---------- monthly ----------
    def _build_monthly(self):
        scroll, lay = _scroll_body()
        bar = QHBoxLayout()
        bar.addWidget(label("Month:", "Muted"))
        self.month = QComboBox()
        self.month.addItems(list(calendar.month_name)[1:])
        self.month.setCurrentIndex(date.today().month - 1)
        self.m_year = QSpinBox()
        self.m_year.setRange(2000, 2100)
        self.m_year.setValue(date.today().year)
        self.month.currentIndexChanged.connect(self.refresh)
        self.m_year.valueChanged.connect(self.refresh)
        bar.addWidget(self.month)
        bar.addWidget(self.m_year)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.m_total = StatCard("Made this month", "wallet", theme.BLUE, theme.BLUE_SOFT)
        self.m_count = StatCard("Sales", "receipt", theme.TEAL_DARK, theme.TEAL_SOFT)
        self.m_avg = StatCard("Daily average", "trend", theme.AMBER, "#FDF3DE")
        self.m_best = StatCard("Best day", "calendar", theme.NAVY, "#E6EBF2")
        _stats_row(lay, [self.m_total, self.m_count, self.m_avg, self.m_best])
        cc = Card("Sales per day")
        self.m_chart = BarChart()
        self.m_chart.setMinimumHeight(250)
        cc.lay.addWidget(self.m_chart)
        lay.addWidget(cc)
        row = QHBoxLayout()
        row.setSpacing(16)
        c1 = Card("Day by day")
        self.m_days = make_table(["Date", "Day", "Sales", "Amount"], 0)
        c1.lay.addWidget(self.m_days)
        c2 = Card("By service")
        self.m_services = make_table(["Service", "Category", "Qty", "Amount", "Share"], 0)
        c2.lay.addWidget(self.m_services)
        c3 = Card("By payment method")
        self.m_pay = make_table(["Method", "Sales", "Amount"], 0)
        c3.lay.addWidget(self.m_pay)
        right = QVBoxLayout()
        right.setSpacing(16)
        right.addWidget(c2)
        right.addWidget(c3)
        right.addStretch(1)
        row.addWidget(c1, 2)
        row.addLayout(right, 3)
        lay.addLayout(row)
        lay.addStretch(1)
        self.tabs.addTab(scroll, "Monthly")

    # ---------- yearly ----------
    def _build_yearly(self):
        scroll, lay = _scroll_body()
        bar = QHBoxLayout()
        bar.addWidget(label("Year:", "Muted"))
        self.year = QSpinBox()
        self.year.setRange(2000, 2100)
        self.year.setValue(date.today().year)
        self.year.valueChanged.connect(self.refresh)
        bar.addWidget(self.year)
        bar.addStretch(1)
        lay.addLayout(bar)
        self.y_total = StatCard("Made this year", "wallet", theme.BLUE, theme.BLUE_SOFT)
        self.y_count = StatCard("Sales", "receipt", theme.TEAL_DARK, theme.TEAL_SOFT)
        self.y_avg = StatCard("Monthly average", "trend", theme.AMBER, "#FDF3DE")
        self.y_best = StatCard("Best month", "calendar", theme.NAVY, "#E6EBF2")
        _stats_row(lay, [self.y_total, self.y_count, self.y_avg, self.y_best])
        cc = Card("Sales per month")
        self.y_chart = BarChart()
        self.y_chart.setMinimumHeight(260)
        cc.lay.addWidget(self.y_chart)
        lay.addWidget(cc)
        c1 = Card("Month by month")
        self.y_months = make_table(["Month", "Sales", "Amount"], 0)
        self.y_months.setMinimumHeight(540)
        c1.lay.addWidget(self.y_months)
        lay.addWidget(c1)
        lay.addStretch(1)
        self.tabs.addTab(scroll, "Yearly")

    # ---------- refresh ----------
    def refresh(self):
        db = self.db
        i = self.tabs.currentIndex()
        if i == 0:
            d = self.day.date().toPython()
            tot, n = db.total_between(d, d)
            self.d_total.set(db.fmt(tot), d.strftime("%A %d %b %Y"))
            self.d_count.set(f"{n:,}", "customers served")
            self.d_avg.set(db.fmt(round(tot / n)) if n else db.fmt(0), "per sale")
            self.d_disc.set(db.fmt(db.discounts_between(d, d)), "already taken off the total")
            _fill_services(db, self.d_services, db.service_breakdown(d, d))
            _fill_payments(db, self.d_pay, db.payment_breakdown(d, d))
        elif i == 1:
            a, b = month_bounds(date(self.m_year.value(), self.month.currentIndex() + 1, 1))
            tot, n = db.total_between(a, b)
            days = db.daily_totals(a, b)
            today = date.today()
            elapsed = (min(b, today) - a).days + 1 if a <= today else 0
            self.m_total.set(db.fmt(tot), a.strftime("%B %Y"))
            self.m_count.set(f"{n:,}", "customers served")
            self.m_avg.set(db.fmt(round(tot / elapsed)) if elapsed > 0 else db.fmt(0),
                           f"over {elapsed} day{'s' if elapsed != 1 else ''}")
            best = max(days, key=lambda x: x[1])
            self.m_best.set(db.fmt(best[1]) if best[1] else "—", best[0].strftime("%A %d %b") if best[1] else "no sales yet")
            hi = (today - a).days if a <= today <= b else -1
            self.m_chart.set_data([(str(d.day), v, f"{d.strftime('%a %d %b')}\n{db.fmt(v)} · {c} sale{'s' if c != 1 else ''}")
                                   for d, v, c in days], highlight_index=hi, label_every=2)
            shown = [x for x in days if x[0] <= today] or days
            self.m_days.setRowCount(len(shown))
            for r, (d, v, c) in enumerate(reversed(shown)):
                self.m_days.setItem(r, 0, cell(d.strftime("%d %b %Y")))
                self.m_days.setItem(r, 1, cell(d.strftime("%A"), color=theme.MUTED))
                self.m_days.setItem(r, 2, cell(f"{c:,}", align_right=True))
                self.m_days.setItem(r, 3, cell(db.fmt(v), align_right=True, bold=bool(v), color=theme.NAVY if v else theme.MUTED))
            self.m_days.setMinimumHeight(min(60 + 40 * len(shown), 900))
            _fill_services(db, self.m_services, db.service_breakdown(a, b))
            _fill_payments(db, self.m_pay, db.payment_breakdown(a, b))
        else:
            y = self.year.value()
            months = db.monthly_totals(y)
            tot = sum(m[1] for m in months)
            n = sum(m[2] for m in months)
            today = date.today()
            elapsed = 12 if y < today.year else today.month if y == today.year else 0
            self.y_total.set(db.fmt(tot), str(y))
            self.y_count.set(f"{n:,}", "customers served")
            self.y_avg.set(db.fmt(round(tot / elapsed)) if elapsed else db.fmt(0), f"over {elapsed} month{'s' if elapsed != 1 else ''}")
            best = max(months, key=lambda x: x[1])
            self.y_best.set(db.fmt(best[1]) if best[1] else "—", calendar.month_name[best[0]] if best[1] else "no sales yet")
            self.y_chart.set_data([(calendar.month_abbr[m], v, f"{calendar.month_name[m]} {y}\n{db.fmt(v)} · {c} sales")
                                   for m, v, c in months], highlight_index=today.month - 1 if y == today.year else -1)
            self.y_months.setRowCount(12)
            for r, (m, v, c) in enumerate(months):
                self.y_months.setItem(r, 0, cell(f"{calendar.month_name[m]} {y}"))
                self.y_months.setItem(r, 1, cell(f"{c:,}", align_right=True))
                self.y_months.setItem(r, 2, cell(db.fmt(v), align_right=True, bold=bool(v), color=theme.NAVY if v else theme.MUTED))

    def export(self):
        db = self.db
        i = self.tabs.currentIndex()
        if i == 0:
            d = self.day.date().toPython()
            name, a, b = f"Daily report {d}", d, d
        elif i == 1:
            a, b = month_bounds(date(self.m_year.value(), self.month.currentIndex() + 1, 1))
            name = f"Monthly report {a.strftime('%Y-%m')}"
        else:
            y = self.year.value()
            a, b, name = date(y, 1, 1), date(y, 12, 31), f"Yearly report {y}"
        path, _ = QFileDialog.getSaveFileName(self, "Export report", name + ".csv", "CSV (*.csv)")
        if not path:
            return
        tot, n = db.total_between(a, b)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([db.setting("business_name")])
            w.writerow([name, f"{a} to {b}"])
            w.writerow([])
            w.writerow(["Total made", tot])
            w.writerow(["Number of sales", n])
            w.writerow(["Discounts given", db.discounts_between(a, b)])
            w.writerow([])
            if i == 2:
                w.writerow(["Month", "Sales", "Amount"])
                for m, v, c in db.monthly_totals(a.year):
                    w.writerow([calendar.month_name[m], c, v])
            else:
                w.writerow(["Date", "Sales", "Amount"])
                for d, v, c in db.daily_totals(a, b):
                    w.writerow([d.isoformat(), c, v])
            w.writerow([])
            w.writerow(["Service", "Category", "Quantity", "Amount"])
            for row in db.service_breakdown(a, b):
                w.writerow(list(row))
            w.writerow([])
            w.writerow(["Payment method", "Amount", "Sales"])
            for row in db.payment_breakdown(a, b):
                w.writerow(list(row))
        QMessageBox.information(self, "Exported", f"Report saved to\n{path}\n\nYou can open it in Excel.")

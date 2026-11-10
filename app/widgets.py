"""Shared widgets: icons, cards, stat tiles, bar chart, table helpers."""
from __future__ import annotations

from PySide6.QtCore import QByteArray, QPoint, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QLayout, QAbstractItemView, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QHeaderView,
                               QLabel, QSizePolicy, QTableWidget, QTableWidgetItem, QToolTip, QVBoxLayout, QWidget)

from . import theme

# Simple stroke icons (24×24 viewBox), drawn for this app.
ICONS = {
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
    "cart": '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2.5 3h3l2.4 11.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L21 7H6.2"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r="1"/><circle cx="3.5" cy="12" r="1"/><circle cx="3.5" cy="18" r="1"/>',
    "tag": '<path d="M20.6 13.4l-7.2 7.2a1.6 1.6 0 0 1-2.3 0L3 12.5V3h9.5l8.1 8.1a1.6 1.6 0 0 1 0 2.3z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "trash": '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5M12 15V3"/>',
    "printer": '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "x": '<path d="M18 6L6 18M6 6l12 12"/>',
    "wallet": '<rect x="2" y="6" width="20" height="14" rx="2"/><path d="M2 10h20M16 15h2"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "receipt": '<path d="M4 2v20l3-2 3 2 3-2 3 2 3-2V2l-3 2-3-2-3 2-3-2-3 2z"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "trend": '<path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.7-4 3-9 3s-9-1.3-9-3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5M12 3v12"/>',
    "folder": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "undo": '<path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-15-6.7L3 13"/>',
}


def icon(name: str, color: str = theme.INK, size: int = 20) -> QIcon:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
           f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    ic = QIcon()
    for scale in (1, 2):
        pm = QPixmap(size * scale, size * scale)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        renderer.render(p)
        p.end()
        pm.setDevicePixelRatio(scale)
        ic.addPixmap(pm)
    return ic


def logo_pixmap(size: int = 40) -> QPixmap:
    """The stacked-layers brand mark."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 46 46">'
           f'<path d="M23 30 L41 21 L41 26 L23 35 L5 26 L5 21 Z" fill="{theme.BLUE}"/>'
           f'<path d="M23 22 L41 13 L41 18 L23 27 L5 18 L5 13 Z" fill="{theme.TEAL}"/>'
           '<path d="M23 4 L41 12 L23 21 L5 12 Z" fill="#FFFFFF"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode()))
    pm = QPixmap(size * 2, size * 2)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    pm.setDevicePixelRatio(2)
    return pm


def label(text: str = "", obj: str | None = None, wrap: bool = False) -> QLabel:
    lb = QLabel(text)
    if obj:
        lb.setObjectName(obj)
    lb.setWordWrap(wrap)
    return lb


def shadow(w: QWidget, blur: int = 24, alpha: int = 18) -> None:
    eff = QGraphicsDropShadowEffect(w)
    eff.setBlurRadius(blur)
    eff.setOffset(0, 4)
    eff.setColor(QColor(10, 37, 64, alpha))
    w.setGraphicsEffect(eff)


class Card(QFrame):
    def __init__(self, title: str = "", parent=None, margins=(20, 18, 20, 18)):
        super().__init__(parent)
        self.setObjectName("Card")
        shadow(self)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(*margins)
        self.lay.setSpacing(12)
        if title:
            self.header = QHBoxLayout()
            self.title_label = label(title, "SectionTitle")
            self.header.addWidget(self.title_label)
            self.header.addStretch(1)
            self.lay.addLayout(self.header)


class StatCard(QFrame):
    def __init__(self, title: str, icon_name: str, accent: str, soft: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        shadow(self)
        self.setMinimumHeight(118)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)
        badge = QLabel()
        badge.setFixedSize(46, 46)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"background:{soft}; border-radius: 12px;")
        badge.setPixmap(icon(icon_name, accent, 22).pixmap(22, 22))
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title = label(title.upper(), "StatLabel")
        self.value = label("—", "StatValue")
        self.hint = label("", "StatHint")
        col.addWidget(self.title)
        col.addWidget(self.value)
        col.addWidget(self.hint)
        lay.addWidget(badge, 0, Qt.AlignTop)
        lay.addLayout(col, 1)

    def set(self, value: str, hint: str = "") -> None:
        self.value.setText(value)
        self.hint.setText(hint)


class BarChart(QWidget):
    """Lightweight bar chart drawn with QPainter (no extra dependencies)."""

    def __init__(self, parent=None, color: str = theme.BLUE, highlight: str = theme.TEAL):
        super().__init__(parent)
        self.data: list[tuple[str, int, str]] = []  # (label, value, tooltip)
        self.color = QColor(color)
        self.highlight = QColor(highlight)
        self.highlight_index = -1
        self.fmt = lambda v: f"{v:,}"
        self.label_every = 1
        self.setMinimumHeight(220)
        self.setMouseTracking(True)
        self._bars: list[QRectF] = []
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, data, highlight_index: int = -1, label_every: int = 1):
        self.data = data
        self.highlight_index = highlight_index
        self.label_every = max(1, label_every)
        self.update()

    @staticmethod
    def _nice_max(v: int) -> int:
        if v <= 0:
            return 1000
        import math
        mag = 10 ** int(math.floor(math.log10(v)))
        for m in (1, 2, 2.5, 5, 10):
            if v <= m * mag:
                return int(m * mag)
        return int(10 * mag)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        left, right, top, bottom = 64, 10, 12, 30
        cw, ch = w - left - right, h - top - bottom
        vmax = self._nice_max(max((d[1] for d in self.data), default=0))
        small = QFont(self.font())
        small.setPointSizeF(8.5)
        p.setFont(small)
        # gridlines
        for i in range(5):
            y = top + ch - ch * i / 4
            p.setPen(QPen(QColor("#E8EDF4"), 1))
            p.drawLine(left, int(y), w - right, int(y))
            p.setPen(QColor(theme.MUTED))
            val = vmax * i / 4
            txt = self._short(val)
            p.drawText(QRectF(0, y - 8, left - 10, 16), Qt.AlignRight | Qt.AlignVCenter, txt)
        self._bars = []
        n = len(self.data)
        if not n:
            p.setPen(QColor(theme.MUTED))
            p.drawText(self.rect(), Qt.AlignCenter, "No sales yet")
            return
        slot = cw / n
        bw = max(3.0, min(38.0, slot * 0.62))
        for i, (lab, val, _tip) in enumerate(self.data):
            x = left + slot * i + (slot - bw) / 2
            bh = ch * (val / vmax) if vmax else 0
            rect = QRectF(x, top + ch - bh, bw, bh)
            self._bars.append(QRectF(left + slot * i, top, slot, ch))
            if val > 0:
                path = QPainterPath()
                r = min(5.0, bw / 2)
                path.addRoundedRect(rect.adjusted(0, 0, 0, r), r, r)
                p.save()
                p.setClipRect(QRectF(x, top, bw, ch))
                p.fillPath(path, self.highlight if i == self.highlight_index else self.color)
                p.restore()
            if i % self.label_every == 0 or i == self.highlight_index:
                p.setPen(QColor(theme.NAVY if i == self.highlight_index else theme.MUTED))
                p.drawText(QRectF(left + slot * i - 20, top + ch + 6, slot + 40, 18), Qt.AlignHCenter | Qt.AlignTop, lab)
        p.end()

    @staticmethod
    def _short(v: float) -> str:
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}m".replace(".0m", "m")
        if v >= 1000:
            return f"{v / 1000:.0f}k"
        return f"{v:.0f}"

    def mouseMoveEvent(self, e):
        for i, r in enumerate(self._bars):
            if r.contains(e.position()):
                QToolTip.showText(e.globalPosition().toPoint(), self.data[i][2], self)
                return
        QToolTip.hideText()


def make_table(headers: list[str], stretch_col: int = 0) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(40)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setSelectionMode(QAbstractItemView.SingleSelection)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.setShowGrid(False)
    t.setFocusPolicy(Qt.NoFocus)
    hh = t.horizontalHeader()
    hh.setHighlightSections(False)
    hh.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    for i in range(len(headers)):
        hh.setSectionResizeMode(i, QHeaderView.Stretch if i == stretch_col else QHeaderView.ResizeToContents)
    return t


def cell(text, align_right: bool = False, bold: bool = False, color: str | None = None, data=None) -> QTableWidgetItem:
    it = QTableWidgetItem(str(text))
    it.setTextAlignment((Qt.AlignRight if align_right else Qt.AlignLeft) | Qt.AlignVCenter)
    if bold:
        f = it.font()
        f.setBold(True)
        it.setFont(f)
    if color:
        it.setForeground(QColor(color))
    if data is not None:
        it.setData(Qt.UserRole, data)
    return it


def hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"color: {theme.LINE}; background: {theme.LINE}; max-height: 1px; border: none;")
    return f


def page_header(title: str, subtitle: str = "") -> tuple[QHBoxLayout, QVBoxLayout]:
    row = QHBoxLayout()
    col = QVBoxLayout()
    col.setSpacing(2)
    col.addWidget(label(title, "PageTitle"))
    if subtitle:
        col.addWidget(label(subtitle, "PageSub"))
    row.addLayout(col)
    row.addStretch(1)
    return row, col


def empty_state(text: str) -> QLabel:
    lb = label(text, "Muted")
    lb.setAlignment(Qt.AlignCenter)
    lb.setMinimumHeight(80)
    return lb


ICON_SIZE = QSize(18, 18)


class FlowLayout(QLayout):
    """Lays children left-to-right and wraps onto new lines (used for category chips)."""

    def __init__(self, parent=None, spacing: int = 8):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(0, 0, 0, 0)
        self._space = spacing

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        s = QSize()
        for it in self._items:
            s = s.expandedTo(it.minimumSize())
        return s

    def _do(self, rect, test):
        x, y, line_h = rect.x(), rect.y(), 0
        for it in self._items:
            hint = it.sizeHint()
            nx = x + hint.width() + self._space
            if nx - self._space > rect.right() and line_h > 0:
                x, y = rect.x(), y + line_h + self._space
                nx, line_h = x + hint.width() + self._space, 0
            if not test:
                it.setGeometry(QRect(QPoint(x, y), hint))
            x, line_h = nx, max(line_h, hint.height())
        return y + line_h - rect.y()

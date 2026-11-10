from __future__ import annotations

import html
from datetime import datetime

from PySide6.QtCore import QMarginsF, Qt
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QTextBrowser, QVBoxLayout)

from . import theme
from .db import Database
from .widgets import ICON_SIZE, icon, label


def receipt_html(db: Database, sale_id: int) -> str:
    s, items = db.sale(sale_id)
    e = html.escape
    when = datetime.strptime(s["created_at"], "%Y-%m-%d %H:%M:%S")
    rows = "".join(
        f"<tr><td>{e(i['service_name'])}<br><span style='color:{theme.MUTED};font-size:9pt'>{i['quantity']} × {db.fmt(i['unit_price'])}</span></td>"
        f"<td align='right' valign='top'>{db.fmt(i['line_total'])}</td></tr>" for i in items)
    subtotal = sum(i["line_total"] for i in items)
    disc = (f"<tr><td>Subtotal</td><td align='right'>{db.fmt(subtotal)}</td></tr>"
            f"<tr><td>Discount</td><td align='right'>−{db.fmt(s['discount'])}</td></tr>") if s["discount"] else ""
    void = (f"<p align='center' style='color:{theme.DANGER};font-weight:bold;font-size:14pt'>VOID — NOT A VALID RECEIPT</p>"
            if s["voided"] else "")
    cust = ""
    if s["customer_name"] or s["customer_phone"]:
        cust = f"<p style='margin:0'>Customer: <b>{e(s['customer_name'] or '—')}</b> {e(s['customer_phone'])}</p>"
    staff = f"<p style='margin:0'>Served by: {e(s['staff'])}</p>" if s["staff"] else ""
    note = f"<p style='margin:6px 0 0;color:{theme.MUTED}'>Note: {e(s['note'])}</p>" if s["note"] else ""
    return f"""
<html><body style="font-family:'Segoe UI','DejaVu Sans',sans-serif;font-size:10.5pt;color:{theme.INK}">
<div align="center">
<p style="margin:0;font-size:15pt;font-weight:bold;color:{theme.NAVY}">{e(db.setting('business_name'))}</p>
<p style="margin:2px 0 0;color:{theme.MUTED}">{e(db.setting('business_address'))}</p>
<p style="margin:0;color:{theme.MUTED}">{e(db.setting('business_phone'))}</p>
<p style="margin:10px 0 0;font-size:11pt;font-weight:bold;letter-spacing:2px;color:{theme.BLUE}">SALES RECEIPT</p>
</div>
{void}
<hr style="border:0;border-top:1px dashed #9AA8BB">
<p style="margin:0">Receipt No: <b>{e(s['receipt_no'])}</b></p>
<p style="margin:0">Date: {when.strftime('%d %b %Y, %I:%M %p')}</p>
{cust}{staff}
<hr style="border:0;border-top:1px dashed #9AA8BB">
<table width="100%" cellspacing="0" cellpadding="4">{rows}</table>
<hr style="border:0;border-top:1px dashed #9AA8BB">
<table width="100%" cellspacing="0" cellpadding="3">
{disc}
<tr><td style="font-size:13pt;font-weight:bold">TOTAL</td><td align="right" style="font-size:13pt;font-weight:bold;color:{theme.NAVY}">{db.fmt(s['total'])}</td></tr>
<tr><td style="color:{theme.MUTED}">Paid by</td><td align="right" style="color:{theme.MUTED}">{e(s['payment_method'])}</td></tr>
</table>
{note}
<hr style="border:0;border-top:1px dashed #9AA8BB">
<p align="center" style="margin:4px 0 0">Thank you for your patronage!</p>
</body></html>"""


class ReceiptDialog(QDialog):
    def __init__(self, db: Database, sale_id: int, parent=None, title: str = "Receipt"):
        super().__init__(parent)
        self.db = db
        self.sale_id = sale_id
        self.setWindowTitle(title)
        self.resize(430, 640)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)
        lay.addWidget(label(title, "SectionTitle"))
        self.view = QTextBrowser()
        self.view.setStyleSheet("background:white; border:1px solid #DDE3EC; border-radius:12px; padding:14px;")
        self.view.setHtml(receipt_html(db, sale_id))
        lay.addWidget(self.view, 1)
        row = QHBoxLayout()
        pdf = QPushButton("  Save PDF")
        pdf.setIcon(icon("download"))
        pdf.setIconSize(ICON_SIZE)
        pdf.clicked.connect(self.save_pdf)
        prn = QPushButton("  Print")
        prn.setIcon(icon("printer"))
        prn.setIconSize(ICON_SIZE)
        prn.clicked.connect(self.print_)
        done = QPushButton("Done")
        done.setObjectName("Primary")
        done.clicked.connect(self.accept)
        row.addWidget(pdf)
        row.addWidget(prn)
        row.addStretch(1)
        row.addWidget(done)
        lay.addLayout(row)

    def _doc(self) -> QTextDocument:
        d = QTextDocument()
        d.setHtml(receipt_html(self.db, self.sale_id))
        return d

    def _setup(self, printer: QPrinter):
        # 80mm receipt-roll friendly width; falls back fine on A4 printers.
        printer.setPageSize(QPageSize(QPageSize.A5))
        printer.setPageMargins(QMarginsF(10, 10, 10, 10), QPageLayout.Millimeter)

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)
        self._setup(printer)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QDialog.Accepted:
            self._doc().print_(printer)

    def save_pdf(self):
        s, _ = self.db.sale(self.sale_id)
        path, _ = QFileDialog.getSaveFileName(self, "Save receipt", f"Receipt-{s['receipt_no']}.pdf", "PDF (*.pdf)")
        if not path:
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        self._setup(printer)
        self._doc().print_(printer)
        QMessageBox.information(self, "Saved", f"Receipt saved to\n{path}")

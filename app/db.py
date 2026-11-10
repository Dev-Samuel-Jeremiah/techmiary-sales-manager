"""SQLite data layer for Techmiary Sales Manager.

All money is stored as integer kobo-free Naira amounts (whole Naira, int) to avoid
floating point errors. Dates are stored as ISO strings (YYYY-MM-DD HH:MM:SS) in local time.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

APP_NAME = "TechmiarySales"


def data_dir() -> Path:
    """Per-user folder that survives app updates (Windows: %APPDATA%, Linux: ~/.local/share)."""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    d = base / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);
CREATE TABLE IF NOT EXISTS services (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL DEFAULT 'General',
    price       INTEGER NOT NULL DEFAULT 0,
    unit        TEXT NOT NULL DEFAULT 'per job',
    description TEXT NOT NULL DEFAULT '',
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sales (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_no     TEXT NOT NULL UNIQUE,
    created_at     TEXT NOT NULL,
    customer_name  TEXT NOT NULL DEFAULT '',
    customer_phone TEXT NOT NULL DEFAULT '',
    payment_method TEXT NOT NULL DEFAULT 'Cash',
    discount       INTEGER NOT NULL DEFAULT 0,
    total          INTEGER NOT NULL DEFAULT 0,
    staff          TEXT NOT NULL DEFAULT '',
    note           TEXT NOT NULL DEFAULT '',
    voided         INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS sale_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id      INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    service_id   INTEGER REFERENCES services(id) ON DELETE SET NULL,
    service_name TEXT NOT NULL,
    category     TEXT NOT NULL DEFAULT 'General',
    unit_price   INTEGER NOT NULL,
    quantity     INTEGER NOT NULL DEFAULT 1,
    line_total   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at);
CREATE INDEX IF NOT EXISTS idx_items_sale ON sale_items(sale_id);
"""

DEFAULT_SETTINGS = {
    "business_name": "Techmiary Technology Concepts",
    "business_address": "Rayfield, Jos, Plateau State",
    "business_phone": "0805 130 1661",
    "currency": "₦",
    "staff_name": "",
}

STARTER_SERVICES = [
    ("Printing (black & white)", "Printing", 100, "per page"),
    ("Printing (colour)", "Printing", 200, "per page"),
    ("Photocopy", "Printing", 50, "per page"),
    ("Scanning", "Printing", 100, "per page"),
    ("Lamination", "Printing", 300, "per sheet"),
    ("Typing", "Documents", 500, "per page"),
    ("Passport photograph", "Photo", 1000, "per set"),
    ("JAMB registration", "Online Registration", 2000, "per job"),
    ("WAEC / NECO registration", "Online Registration", 2000, "per job"),
    ("NIN slip printing", "Online Registration", 1000, "per job"),
    ("Graphics design (flyer)", "Design", 5000, "per job"),
    ("Computer repair", "Repairs", 5000, "per job"),
]


def money(amount: int, symbol: str = "₦") -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}{symbol}{abs(int(amount)):,}"


@dataclass
class Service:
    id: int
    name: str
    category: str
    price: int
    unit: str
    description: str
    active: bool


class Database:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else data_dir() / "techmiary_sales.db"
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.executescript(SCHEMA)
        for k, v in DEFAULT_SETTINGS.items():
            self.conn.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (k, v))
        self.conn.commit()

    # ---------- settings ----------
    def setting(self, key: str) -> str:
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else DEFAULT_SETTINGS.get(key, "")

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute("INSERT INTO settings(key, value) VALUES (?, ?) "
                          "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        self.conn.commit()

    @property
    def currency(self) -> str:
        return self.setting("currency") or "₦"

    def fmt(self, amount: int) -> str:
        return money(amount, self.currency)

    # ---------- services ----------
    def is_empty(self) -> bool:
        return self.conn.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0

    def seed_starter_services(self) -> None:
        now = _now()
        self.conn.executemany(
            "INSERT INTO services(name, category, price, unit, created_at) VALUES (?,?,?,?,?)",
            [(n, c, p, u, now) for n, c, p, u in STARTER_SERVICES])
        self.conn.commit()

    def services(self, search: str = "", include_inactive: bool = True, category: str = "") -> list[Service]:
        q = "SELECT * FROM services WHERE 1=1"
        args: list = []
        if search:
            q += " AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"
            args += [f"%{search}%"] * 3
        if not include_inactive:
            q += " AND active=1"
        if category:
            q += " AND category=?"
            args.append(category)
        q += " ORDER BY category COLLATE NOCASE, name COLLATE NOCASE"
        return [Service(r["id"], r["name"], r["category"], r["price"], r["unit"], r["description"], bool(r["active"]))
                for r in self.conn.execute(q, args)]

    def categories(self) -> list[str]:
        rows = self.conn.execute("SELECT DISTINCT category FROM services ORDER BY category COLLATE NOCASE")
        return [r[0] for r in rows]

    def add_service(self, name: str, category: str, price: int, unit: str, description: str = "", active: bool = True) -> int:
        cur = self.conn.execute(
            "INSERT INTO services(name, category, price, unit, description, active, created_at) VALUES (?,?,?,?,?,?,?)",
            (name.strip(), category.strip() or "General", int(price), unit.strip() or "per job", description.strip(), int(active), _now()))
        self.conn.commit()
        return cur.lastrowid

    def update_service(self, sid: int, name: str, category: str, price: int, unit: str, description: str, active: bool) -> None:
        self.conn.execute(
            "UPDATE services SET name=?, category=?, price=?, unit=?, description=?, active=? WHERE id=?",
            (name.strip(), category.strip() or "General", int(price), unit.strip() or "per job", description.strip(), int(active), sid))
        self.conn.commit()

    def delete_service(self, sid: int) -> bool:
        """Deletes a service if it was never sold; otherwise marks it inactive. Returns True if deleted."""
        used = self.conn.execute("SELECT COUNT(*) FROM sale_items WHERE service_id=?", (sid,)).fetchone()[0]
        if used:
            self.conn.execute("UPDATE services SET active=0 WHERE id=?", (sid,))
            self.conn.commit()
            return False
        self.conn.execute("DELETE FROM services WHERE id=?", (sid,))
        self.conn.commit()
        return True

    # ---------- sales ----------
    def _next_receipt_no(self, when: datetime) -> str:
        prefix = when.strftime("TM%y%m%d-")
        row = self.conn.execute("SELECT receipt_no FROM sales WHERE receipt_no LIKE ? ORDER BY id DESC LIMIT 1",
                                (prefix + "%",)).fetchone()
        n = int(row[0].split("-")[1]) + 1 if row else 1
        return f"{prefix}{n:03d}"

    def record_sale(self, items: list[dict], customer_name: str = "", customer_phone: str = "",
                    payment_method: str = "Cash", discount: int = 0, note: str = "",
                    when: datetime | None = None) -> tuple[int, str]:
        """items: [{service_id, service_name, category, unit_price, quantity}]"""
        if not items:
            raise ValueError("A sale needs at least one service.")
        when = when or datetime.now()
        subtotal = sum(int(i["unit_price"]) * int(i["quantity"]) for i in items)
        discount = max(0, min(int(discount), subtotal))
        total = subtotal - discount
        receipt = self._next_receipt_no(when)
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO sales(receipt_no, created_at, customer_name, customer_phone, payment_method, discount, total, staff, note) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (receipt, when.strftime("%Y-%m-%d %H:%M:%S"), customer_name.strip(), customer_phone.strip(),
                 payment_method, discount, total, self.setting("staff_name"), note.strip()))
            sale_id = cur.lastrowid
            self.conn.executemany(
                "INSERT INTO sale_items(sale_id, service_id, service_name, category, unit_price, quantity, line_total) VALUES (?,?,?,?,?,?,?)",
                [(sale_id, i.get("service_id"), i["service_name"], i.get("category", "General"), int(i["unit_price"]),
                  int(i["quantity"]), int(i["unit_price"]) * int(i["quantity"])) for i in items])
        return sale_id, receipt

    def void_sale(self, sale_id: int, voided: bool = True) -> None:
        self.conn.execute("UPDATE sales SET voided=? WHERE id=?", (int(voided), sale_id))
        self.conn.commit()

    def sale(self, sale_id: int) -> tuple[sqlite3.Row, list[sqlite3.Row]]:
        s = self.conn.execute("SELECT * FROM sales WHERE id=?", (sale_id,)).fetchone()
        items = self.conn.execute("SELECT * FROM sale_items WHERE sale_id=? ORDER BY id", (sale_id,)).fetchall()
        return s, items

    def sales_between(self, start: date, end: date, search: str = "", include_voided: bool = True,
                      payment: str = "") -> list[sqlite3.Row]:
        """Sales from start (inclusive) to end (inclusive)."""
        q = ("SELECT s.*, (SELECT GROUP_CONCAT(service_name || CASE WHEN quantity>1 THEN ' ×' || quantity ELSE '' END, ', ') "
             "FROM sale_items WHERE sale_id=s.id) AS summary FROM sales s WHERE created_at >= ? AND created_at < ?")
        args: list = [start.isoformat(), (end + timedelta(days=1)).isoformat()]
        if search:
            q += (" AND (s.customer_name LIKE ? OR s.customer_phone LIKE ? OR s.receipt_no LIKE ? OR "
                  "s.id IN (SELECT sale_id FROM sale_items WHERE service_name LIKE ?))")
            args += [f"%{search}%"] * 4
        if not include_voided:
            q += " AND s.voided=0"
        if payment:
            q += " AND s.payment_method=?"
            args.append(payment)
        q += " ORDER BY s.created_at DESC, s.id DESC"
        return self.conn.execute(q, args).fetchall()

    # ---------- reports ----------
    def total_between(self, start: date, end: date) -> tuple[int, int]:
        """(revenue, number of sales) excluding voided sales."""
        r = self.conn.execute(
            "SELECT COALESCE(SUM(total),0), COUNT(*) FROM sales WHERE voided=0 AND created_at >= ? AND created_at < ?",
            (start.isoformat(), (end + timedelta(days=1)).isoformat())).fetchone()
        return int(r[0]), int(r[1])

    def daily_totals(self, start: date, end: date) -> list[tuple[date, int, int]]:
        rows = {r[0]: (int(r[1]), int(r[2])) for r in self.conn.execute(
            "SELECT substr(created_at,1,10) d, SUM(total), COUNT(*) FROM sales WHERE voided=0 AND created_at >= ? AND created_at < ? GROUP BY d",
            (start.isoformat(), (end + timedelta(days=1)).isoformat()))}
        out, d = [], start
        while d <= end:
            t, c = rows.get(d.isoformat(), (0, 0))
            out.append((d, t, c))
            d += timedelta(days=1)
        return out

    def monthly_totals(self, year: int) -> list[tuple[int, int, int]]:
        rows = {int(r[0]): (int(r[1]), int(r[2])) for r in self.conn.execute(
            "SELECT substr(created_at,6,2) m, SUM(total), COUNT(*) FROM sales WHERE voided=0 AND substr(created_at,1,4)=? GROUP BY m",
            (f"{year:04d}",))}
        return [(m, *rows.get(m, (0, 0))) for m in range(1, 13)]

    def service_breakdown(self, start: date, end: date) -> list[tuple[str, str, int, int]]:
        """[(service, category, quantity, revenue)] ordered by revenue. Discounts are not spread over lines."""
        return [(r[0], r[1], int(r[2]), int(r[3])) for r in self.conn.execute(
            "SELECT i.service_name, i.category, SUM(i.quantity), SUM(i.line_total) FROM sale_items i JOIN sales s ON s.id=i.sale_id "
            "WHERE s.voided=0 AND s.created_at >= ? AND s.created_at < ? GROUP BY i.service_name, i.category ORDER BY 4 DESC",
            (start.isoformat(), (end + timedelta(days=1)).isoformat()))]

    def payment_breakdown(self, start: date, end: date) -> list[tuple[str, int, int]]:
        return [(r[0], int(r[1]), int(r[2])) for r in self.conn.execute(
            "SELECT payment_method, SUM(total), COUNT(*) FROM sales WHERE voided=0 AND created_at >= ? AND created_at < ? "
            "GROUP BY payment_method ORDER BY 2 DESC", (start.isoformat(), (end + timedelta(days=1)).isoformat()))]

    def discounts_between(self, start: date, end: date) -> int:
        return int(self.conn.execute(
            "SELECT COALESCE(SUM(discount),0) FROM sales WHERE voided=0 AND created_at >= ? AND created_at < ?",
            (start.isoformat(), (end + timedelta(days=1)).isoformat())).fetchone()[0])

    # ---------- backup ----------
    def backup_to(self, target: Path) -> None:
        dest = sqlite3.connect(target)
        with dest:
            self.conn.backup(dest)
        dest.close()

    def restore_from(self, source: Path) -> None:
        test = sqlite3.connect(source)
        names = {r[0] for r in test.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        test.close()
        if not {"services", "sales", "sale_items"} <= names:
            raise ValueError("That file is not a Techmiary Sales backup.")
        self.conn.close()
        safety = self.path.with_suffix(".before-restore.db")
        shutil.copy2(self.path, safety)
        for ext in ("-wal", "-shm"):
            p = Path(str(self.path) + ext)
            if p.exists():
                p.unlink()
        shutil.copy2(source, self.path)
        self.__init__(self.path)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def month_bounds(d: date) -> tuple[date, date]:
    start = d.replace(day=1)
    nxt = (start + timedelta(days=32)).replace(day=1)
    return start, nxt - timedelta(days=1)

"""Colours and the application style sheet (Techmiary brand: navy, blue, teal)."""

NAVY = "#0A2540"
NAVY_2 = "#12325A"
BLUE = "#1B4DFF"
BLUE_SOFT = "#E8EEFF"
TEAL = "#00B8A9"
TEAL_DARK = "#00897E"
TEAL_SOFT = "#E0F7F5"
INK = "#1F2D3D"
MUTED = "#5B6B80"
LINE = "#DDE3EC"
BG = "#F4F7FB"
CARD = "#FFFFFF"
DANGER = "#D64545"
DANGER_SOFT = "#FDECEC"
AMBER = "#E8A317"

_STYLE = f"""
* {{
    font-family: "Segoe UI", "Inter", "Ubuntu", "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 13px;
    color: {INK};
}}
QMainWindow, QWidget#Page {{ background: {BG}; }}
QWidget#Sidebar {{ background: {NAVY}; }}
QLabel#BrandName {{ color: white; font-size: 17px; font-weight: 700; }}
QLabel#BrandSub {{ color: #9FE9E2; font-size: 10px; letter-spacing: 2px; }}
QLabel#SideFoot {{ color: #8FA3BF; font-size: 11px; }}
QPushButton#NavButton {{
    color: #C9D4E5; background: transparent; border: none; text-align: left;
    padding: 11px 16px; border-radius: 9px; font-size: 13.5px; font-weight: 600;
}}
QPushButton#NavButton:hover {{ background: {NAVY_2}; color: white; }}
QPushButton#NavButton:checked {{ background: {BLUE}; color: white; }}

QLabel#PageTitle {{ font-size: 24px; font-weight: 700; color: {NAVY}; }}
QLabel#PageSub {{ color: {MUTED}; font-size: 13px; }}
QLabel#SectionTitle {{ font-size: 15px; font-weight: 700; color: {NAVY}; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Small {{ color: {MUTED}; font-size: 11px; }}

QFrame#Card {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; }}
QFrame#StatCard {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; }}
QLabel#StatLabel {{ color: {MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1px; }}
QLabel#StatValue {{ color: {NAVY}; font-size: 26px; font-weight: 800; }}
QLabel#StatHint {{ color: {MUTED}; font-size: 12px; }}
QFrame#TotalPanel {{ background: {NAVY}; border-radius: 14px; }}
QLabel#TotalLabel {{ color: #9FE9E2; font-size: 11px; font-weight: 700; letter-spacing: 1px; }}
QLabel#TotalValue {{ color: white; font-size: 32px; font-weight: 800; }}
QLabel#TotalSmall {{ color: #C9D4E5; font-size: 12px; }}

QPushButton {{
    background: white; border: 1px solid {LINE}; border-radius: 9px; padding: 8px 14px; font-weight: 600;
}}
QPushButton:hover {{ border-color: {BLUE}; color: {BLUE}; }}
QPushButton:disabled {{ color: #A8B3C2; border-color: {LINE}; }}
QPushButton#Primary {{ background: {BLUE}; color: white; border: 1px solid {BLUE}; }}
QPushButton#Primary:hover {{ background: #163FD6; color: white; }}
QPushButton#Primary:disabled {{ background: #A9B9F5; border-color: #A9B9F5; color: white; }}
QPushButton#Success {{ background: {TEAL_DARK}; color: white; border: 1px solid {TEAL_DARK}; font-size: 15px; padding: 12px 18px; }}
QPushButton#Success:hover {{ background: #00756C; color: white; }}
QPushButton#Success:disabled {{ background: #9BD3CE; border-color: #9BD3CE; color: white; }}
QPushButton#Danger {{ color: {DANGER}; }}
QPushButton#Danger:disabled {{ color: #E6A3A3; }}
QPushButton#Danger:hover {{ background: {DANGER_SOFT}; border-color: {DANGER}; color: {DANGER}; }}
QPushButton#Chip {{ border-radius: 15px; padding: 6px 13px; font-weight: 600; color: {MUTED}; }}
QPushButton#Chip:checked {{ background: {NAVY}; color: white; border-color: {NAVY}; }}
QPushButton#Seg {{ border-radius: 9px; padding: 9px 10px; }}
QPushButton#Seg:checked {{ background: {BLUE_SOFT}; color: {BLUE}; border: 1.5px solid {BLUE}; }}
QToolButton#ServiceTile {{
    background: white; border: 1px solid {LINE}; border-radius: 12px; padding: 10px; text-align: left;
}}
QToolButton#ServiceTile:hover {{ border: 1.5px solid {BLUE}; background: #FAFCFF; }}

QLineEdit, QSpinBox, QComboBox, QDateEdit, QDateTimeEdit, QTextEdit, QPlainTextEdit {{
    background: white; border: 1px solid {LINE}; border-radius: 9px; padding: 7px 10px;
    selection-background-color: {BLUE};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QPlainTextEdit:focus {{
    border: 1.5px solid {BLUE};
}}
QComboBox::drop-down, QDateEdit::drop-down, QDateTimeEdit::drop-down {{ border: none; width: 26px; }}
QComboBox::down-arrow, QDateEdit::down-arrow, QDateTimeEdit::down-arrow {{ image: url(@DOWN@); width: 12px; height: 12px; }}
QSpinBox::up-button {{ subcontrol-origin: border; subcontrol-position: top right; width: 20px; border: none; background: transparent; margin-top: 3px; }}
QSpinBox::down-button {{ subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; border: none; background: transparent; margin-bottom: 3px; }}
QSpinBox::up-arrow {{ image: url(@UP@); width: 10px; height: 10px; }}
QSpinBox::down-arrow {{ image: url(@DOWN@); width: 10px; height: 10px; }}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {BLUE_SOFT}; border-radius: 4px; }}
QComboBox QAbstractItemView {{ border: 1px solid {LINE}; selection-background-color: {BLUE_SOFT}; selection-color: {INK}; }}

QTableWidget, QTableView {{
    background: white; border: none; gridline-color: transparent;
    selection-background-color: {BLUE_SOFT}; selection-color: {INK}; alternate-background-color: #F9FBFD;
}}
QTableWidget::item, QTableView::item {{ padding: 6px; border-bottom: 1px solid #EEF2F7; }}
QHeaderView::section {{
    background: white; color: {MUTED}; font-size: 11px; font-weight: 700; padding: 9px 6px;
    border: none; border-bottom: 1.5px solid {LINE}; text-transform: uppercase;
}}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{
    background: transparent; color: {MUTED}; padding: 9px 18px; font-weight: 700; border-bottom: 2.5px solid transparent;
}}
QTabBar::tab:selected {{ color: {BLUE}; border-bottom: 2.5px solid {BLUE}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #C5CFDC; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #C5CFDC; border-radius: 4px; min-width: 30px; }}
QCheckBox {{ spacing: 8px; }}
QToolTip {{ background: {NAVY}; color: white; border: none; padding: 6px; border-radius: 6px; }}
QMessageBox QLabel {{ font-size: 13px; }}
QDialog {{ background: {BG}; }}
"""


def build_style() -> str:
    """Writes the small arrow images Qt style sheets need, then returns the finished style sheet."""
    import tempfile
    from pathlib import Path
    from PySide6.QtCore import QByteArray, Qt
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
    d = Path(tempfile.gettempdir()) / "techmiary_sales_ui"
    d.mkdir(exist_ok=True)
    paths = {}
    for name, path in (("down", "M6 9l6 6 6-6"), ("up", "M6 15l6-6 6 6")):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" '
               f'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></svg>')
        img = QImage(48, 48, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        p = QPainter(img)
        QSvgRenderer(QByteArray(svg.encode())).render(p)
        p.end()
        f = d / f"{name}.png"
        img.save(str(f))
        paths[name] = f.as_posix()
    return _STYLE.replace("@DOWN@", paths["down"]).replace("@UP@", paths["up"])

# Techmiary Sales Manager

A desktop program for recording the services Techmiary renders to customers, so the shop no longer
keeps sales on paper. It works on **Windows** and **Linux**, offline, with all records saved on the computer.

## What it does

| Screen | What you do there |
|---|---|
| **Dashboard** | See today's takings, customers served today, this month's total, the daily average, a 30‑day sales chart, the top services this month and the latest sales. |
| **New sale** | Tap services to add them to the sale, change the price or quantity if needed, add the customer's name/phone (optional), pick Cash / Transfer / POS, give a discount, then **Complete sale**. A receipt opens that you can print or save as PDF. Use **Custom item** for a one‑off job that is not on your list. To enter an old sale from your paper records, change the date and time before completing it. |
| **Sales history** | Every sale, filtered by Today / Yesterday / This week / This month / Last month / This year or any dates. Search by customer, phone, receipt number or service. View or reprint a receipt, void a sale entered by mistake (it stops counting in totals but stays on record), and export to CSV for Excel. |
| **Services & prices** | Add, edit and remove the services you offer, with category, price and how it is charged (per page, per job…). A service already used in past sales is marked *unavailable* instead of deleted, so old records stay complete. |
| **Reports** | **Daily** – what the shop made on any day, by service and by payment method. **Monthly** – month total, daily average, best day, a per‑day chart and table, by service and payment method. **Yearly** – month by month. Each report exports to CSV. |
| **Settings** | Business name, address, phone and cashier name for receipts; currency symbol; **Back up now**, **Restore from a backup**, and open the data folder. |

Keyboard shortcuts: **Ctrl+N** new sale, **Ctrl+1** dashboard, **Ctrl+3** history, **Ctrl+4** services,
**Ctrl+5** reports, **Ctrl+6** settings. On the New sale screen, type in the search box and press **Enter** to add the first match.

## Where the records are kept

* Windows: `%APPDATA%\TechmiarySales\techmiary_sales.db`
* Linux: `~/.local/share/TechmiarySales/techmiary_sales.db`

Updating or reinstalling the program does not touch this file. Use **Settings → Back up now** regularly
(for example every Friday) and keep the backup on a flash drive or Google Drive.

## Running it

### Linux (ready-made program)
The `TechmiarySales` file in the Linux download is ready to run:

```bash
chmod +x TechmiarySales
./TechmiarySales
./install_linux.sh        # optional: adds it to your applications menu
```

### Windows – build the .exe once
1. Install Python 3.10 or newer from python.org. On the first installer screen tick **Add python.exe to PATH**.
2. Double‑click **build_windows.bat** in this folder and wait (it downloads what it needs, about 5 minutes).
3. Your program is `dist\TechmiarySales.exe`. Copy it to the Desktop and double‑click to run.

### Run from source (any system)
```bash
pip install -r requirements.txt
python main.py
```

### Optional: let GitHub build both versions
Push this folder to a GitHub repository. The workflow in `.github/workflows/build.yml` builds
`TechmiarySales.exe` (Windows) and `TechmiarySales` (Linux); download them from the run's **Artifacts**.

## Project layout

```
main.py                 start-up
app/db.py               SQLite database: services, sales, reports, backup/restore
app/theme.py            Techmiary colours and style sheet
app/widgets.py          icons, cards, stat tiles, bar chart, tables
app/main_window.py      sidebar and page switching
app/page_*.py           Dashboard, New sale, Sales history, Services, Reports, Settings
app/receipt.py          receipt view, print and PDF
assets/                 app icon (.png, .ico)
```

Amounts are stored as whole Naira. Built with Python, PySide6 (Qt) and SQLite.

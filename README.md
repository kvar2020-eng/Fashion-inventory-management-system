# Fashion Inventory Management System

A Python desktop application for fashion-retail inventory management, barcode-based sales tracking, and stock/sales charts.

> **Reconstruction notice:** The original `.py` files were unavailable. This repository package is a clean reconstruction from the source-code screenshots and feature descriptions in the accompanying project report. It is not an exact recovery of the original source. It has not been run against your local MySQL setup; please test it before presenting it as a working release.

## Features represented
- Account signup and login (passwords hashed with PBKDF2 in this reconstruction)
- Add, update, delete, and search inventory records
- Filter by type, size, color, and supplier
- Unique barcode validation
- Barcode sale tracking with stock decrement
- Stock quantity and items-sold charts

## Stack
Python 3.13+, Tkinter/ttk, MySQL 8, mysql-connector-python, Matplotlib.

## Run locally
1. Install Python and MySQL Server.
2. Create and activate a virtual environment.
3. Install packages: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`, then set your MySQL credentials as environment variables (or export them in your shell). Never commit real credentials.
5. Run `python app.py`.

The configured MySQL user must have permission to create the configured database and tables.

## Files
- `app.py` — Tkinter user interface
- `database.py` — MySQL connection and schema setup
- `inventory.py` — inventory CRUD and sales
- `login.py` — registration and login helpers
- `requirements.txt` — dependencies
- `.env.example` — safe configuration template

## Known gaps
The report mentions CSV export and a Pandas-based reporting module; those are not implemented in this first reconstruction. The original report also documents password reset screens, which are not yet connected in this GUI. This is a local desktop app, not a hosted website.

## Credit
Project report title: **Fashion Inventory Management System**. The report lists **K. Varsha** as a team member. Please add the exact team member names and your own contribution before using this as a portfolio submission.

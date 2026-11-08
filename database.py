
import sqlite3
from datetime import datetime


DATABASE_NAME = "workflow_history.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    """Create database tables if they do not exist."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS workflow_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                filename TEXT,
                vendor TEXT,
                invoice_number TEXT,
                invoice_date TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'Processing',
                uploaded_at TEXT
            )
        """)


def save_event(invoice_id, action, details):
    """Save one workflow event."""

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO workflow_history (
                invoice_id, timestamp, action, details
            )
            VALUES (?, ?, ?, ?)
        """, (invoice_id, timestamp, action, details))


def get_events(invoice_id):
    """Retrieve workflow events for one invoice."""

    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT timestamp, action, details
            FROM workflow_history
            WHERE invoice_id = ?
            ORDER BY id ASC
        """, (invoice_id,))

        rows = cursor.fetchall()

    return [
        {
            "timestamp": row[0],
            "action": row[1],
            "details": row[2],
        }
        for row in rows
    ]


def save_invoice(invoice_id, filename, invoice_data):
    """Save or update an invoice in the archive."""

    uploaded_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO invoices (
                invoice_id,
                filename,
                vendor,
                invoice_number,
                invoice_date,
                total_amount,
                status,
                uploaded_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(invoice_id) DO UPDATE SET
                filename = excluded.filename,
                vendor = excluded.vendor,
                invoice_number = excluded.invoice_number,
                invoice_date = excluded.invoice_date,
                total_amount = excluded.total_amount
        """, (
            invoice_id,
            filename,
            invoice_data.get("vendor", ""),
            invoice_data.get("invoice_number", ""),
            invoice_data.get("invoice_date", ""),
            invoice_data.get("total_amount", 0),
            "Processing",
            uploaded_at,
        ))


def update_invoice_status(invoice_id, status):
    """Update the approval status of an invoice."""

    with get_connection() as connection:
        connection.execute("""
            UPDATE invoices
            SET status = ?
            WHERE invoice_id = ?
        """, (status, invoice_id))


def get_invoice_archive():
    """Retrieve all archived invoices."""

    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT
                invoice_id,
                filename,
                vendor,
                invoice_number,
                invoice_date,
                total_amount,
                status,
                uploaded_at
            FROM invoices
            ORDER BY uploaded_at DESC
        """)

        rows = cursor.fetchall()

    columns = [
        "invoice_id",
        "filename",
        "vendor",
        "invoice_number",
        "invoice_date",
        "total_amount",
        "status",
        "uploaded_at",
    ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]

from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
from pathlib import Path

DATABASE_PATH = os.getenv("DATABASE_PATH")


def _get_connection():
    """Return a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database and create table if not exists."""
    db_path = Path(DATABASE_PATH)
    
    # Create parent directory if needed
    if db_path.parent and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {db_path.parent}")
    
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_requests (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    service_selected TEXT NOT NULL,
                    description TEXT,
                    original_filename TEXT NOT NULL,
                    total_rows INTEGER NOT NULL,
                    total_columns INTEGER NOT NULL,
                    duplicate_rows INTEGER NOT NULL,
                    column_info TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database and table ready.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def save_request(
    request_id: str,
    name: str,
    email: str,
    service_selected: str,
    description: str,
    original_filename: str,
    total_rows: int,
    total_columns: int,
    duplicate_rows: int,
    column_info: str
) -> bool:
    """Save analysis request to database. Returns True on success."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_requests (
                    id, name, email, service_selected, description,
                    original_filename, total_rows, total_columns,
                    duplicate_rows, column_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_id, name, email, service_selected, description,
                original_filename, total_rows, total_columns,
                duplicate_rows, column_info
            ))
            conn.commit()
            print(f"Request {request_id} saved to database.")
            return True
    except Exception as e:
        print(f"Error saving request: {e}")
        return False


def get_request(request_id: str) -> dict | None:
    """Retrieve analysis request by ID. Returns dict or None if not found."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM analysis_requests WHERE id = ?", (request_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"Error retrieving request: {e}")
        return None


# DataCheck — CSV Data Quality Analyzer

A lightweight web application that analyzes CSV files for common data quality issues.
Built as a hiring assessment project demonstrating full-stack Python development.

**Current status**: Planning complete. Implementation not started. Not yet deployed.

---

## Overview

DataCheck accepts a service request form with a CSV upload, analyzes the file for basic
data quality metrics, persists the request and results in a database, and returns a
downloadable JSON report.

### Problem statement

Data analysts frequently work with CSV files that contain hidden quality issues — missing
values, duplicate rows, or columns with unexpected data types. DataCheck provides a quick,
zero-configuration analysis to surface these issues without modifying the original data.

### Intended users

- Data analysts and engineers checking CSV quality before processing
- Hiring managers evaluating this technical assessment submission

---

## Features

- Service request form (name, email, service selection, description, CSV upload)
- CSV analysis: row count, column count, per-column missing value counts and percentages,
  duplicate row count, column names, inferred data types
- Downloadable JSON analysis report
- Persistent storage of requests and analysis summaries
- User-friendly error handling and validation

---

## Technology stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| CSV processing | pandas |
| Database | SQLite (file-based) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Hosting | PythonAnywhere free tier |

---

## Architecture overview

```
Browser
  │
  ├── GET /          → HTML form (served by FastAPI + Jinja2 templates)
  │
  └── POST /api/analyze
        │
        ├── Validate form fields (Pydantic)
        ├── Validate file (size, extension, parseable CSV)
        ├── Analyze CSV in memory (pandas) — file discarded after analysis
        ├── Write record to SQLite (request + analysis summary JSON)
        └── Return analysis result → frontend renders results + download link

GET /api/download/{request_id} → returns stored JSON as a file download
GET /health                    → health check
```

Data flow:
- Uploaded CSV is loaded into memory, analyzed, then discarded
- Only form fields and the analysis summary are persisted in SQLite
- CSV file contents and raw rows are never stored or logged

---

## Project structure

```
datacheck/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── analyzer.py          # CSV analysis logic
│   ├── schemas.py           # Pydantic request/response models
│   ├── models.py            # SQLAlchemy ORM models
│   ├── database.py          # SQLite connection and session management
│   ├── templates/
│   │   └── index.html       # Service request form
│   └── static/
│       ├── styles.css
│       └── app.js
├── tests/
│   ├── test_analyzer.py
│   └── test_api.py
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── AI_LOG.md
│   ├── TEST_PLAN.md
│   ├── DECISIONS.md
│   └── DEPLOYMENT.md
├── AGENTS.md
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Prerequisites

- Python 3.11+
- pip
- Git

---

## Local setup

> These instructions will be verified and completed during implementation.
> The commands below are the intended setup; they have not been tested yet.

### 1. Clone the repository

```bash
git clone https://github.com/irmakburkay/datacheck.git
cd datacheck
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your local values
```

### 5. Initialize the database

The database is created automatically on first startup. The SQLite file will be placed
at the path specified by `DATABASE_PATH` in your `.env` file.

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Running tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v
```

See `docs/TEST_PLAN.md` for the full list of test cases and their current status.

---

## Environment variables

See `.env.example` for the complete list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_PATH` | — | Absolute or relative path to the SQLite file |
| `MAX_UPLOAD_SIZE` | `5242880` | Maximum CSV upload size in bytes (default 5 MB) |
| `MAX_ROWS` | `100000` | Maximum rows accepted in an uploaded CSV |
| `MAX_COLUMNS` | `100` | Maximum columns accepted |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve the service request form |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/api/analyze` | Submit service request + CSV; returns analysis result |
| `GET` | `/api/download/{id}` | Download analysis as JSON file |

### POST /api/analyze

**Request**: `multipart/form-data`

| Field | Type | Required |
|---|---|---|
| `name` | string | Yes |
| `email` | valid email | Yes |
| `service` | string | Yes |
| `description` | string | No |
| `csv_file` | file (.csv, ≤5 MB) | Yes |

**Success response** (HTTP 200):

```json
{
  "request_id": "uuid-string",
  "status": "success",
  "analysis": {
    "filename": "example.csv",
    "total_rows": 1000,
    "total_columns": 5,
    "duplicate_rows": 5,
    "columns": [
      {
        "name": "user_id",
        "data_type": "integer",
        "missing_count": 0,
        "missing_percentage": 0.0
      }
    ]
  },
  "download_url": "/api/download/uuid-string"
}
```

**Error response** (HTTP 400/422/500):

```json
{
  "error": "Validation error",
  "message": "A valid email address is required."
}
```

---

## CSV analysis — metric definitions

| Metric | Definition |
|---|---|
| Total rows | Count of data rows, excluding the header |
| Total columns | Count of columns from the header row |
| Duplicate rows | Rows where every column value is identical to another row |
| Missing count | Empty strings and null values per column |
| Missing percentage | `missing_count / total_rows × 100` |
| Data type | Inferred per column: integer, float, date, boolean, or string |

Data type detection is best-effort. String is the fallback for columns that do not
match a more specific type.

---

## Input validation and file restrictions

- File must have a `.csv` extension
- File content must be parseable as CSV (extension alone is not sufficient)
- Maximum file size: 5 MB by default (configurable via `MAX_UPLOAD_SIZE`)
- Maximum rows: 100,000 (configurable via `MAX_ROWS`)
- Maximum columns: 100 (configurable via `MAX_COLUMNS`)
- Name, email, and service selection are required form fields
- Email format is validated server-side

---

## Data collected

This application collects and stores:
- Name and email address (from the service request form)
- Service selection and description
- Original filename of the uploaded CSV
- Analysis summary (aggregated metrics only — no CSV contents)
- Submission timestamp

CSV file contents are processed in memory and discarded. They are never written to disk
or stored in the database.

---

## Deployment

See `docs/DEPLOYMENT.md` for full deployment instructions.

**Live URL**: Not yet deployed.

Target platform: PythonAnywhere free Beginner tier (`username.pythonanywhere.com`).
ASGI compatibility must be verified before deployment proceeds.

---

## Known limitations

- SQLite is not suitable for high-concurrency production use
- PythonAnywhere free tier has restricted outbound internet access
- ASGI support on PythonAnywhere is a beta feature — stability not guaranteed
- No authentication or access control
- No data deletion or retention management

---

## License

MIT License — see `LICENSE` for details.

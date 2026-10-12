# DataCheck — CSV Data Quality Analyzer

A lightweight web application that analyzes CSV files for common data quality issues.
Built as a hiring assessment project development.

**Current status**: Live and verified on PythonAnywhere (Flask/WSGI). UI redesigned, custom error pages added, all endpoints operational.

**Live URL**: https://irmakburkay.pythonanywhere.com/

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
  duplicate row count, column names, inferred data types, unique counts, statistical metrics
  (min/max/mean/median for numeric), date ranges (earliest/latest for dates)
- Downloadable JSON analysis report with one-click download button
- Rate limiting (10 requests per minute per IP) for DDoS protection
- Persistent storage of requests and analysis summaries
- Professional UI with landing page design and illustrated error pages
- User-friendly error handling and validation

---

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python 3.11+) |
| CSV processing | pandas |
| Database | SQLite (file-based) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Hosting | PythonAnywhere free Beginner tier |

---

## Architecture overview

```
Browser
  │
  ├── GET /          → HTML form (served by Flask + Jinja2 templates)
  │
  └── POST /api/analyze
        │
        ├── Validate form fields (manual validation)
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

## Project Structure

```
datacheck/
├── app/
│   ├── main.py              # Flask application (routes, error handlers)
│   ├── analyzer.py          # CSV analysis logic
│   ├── database.py          # SQLite connection and operations
│   ├── rate_limiter.py      # Rate limiting implementation
│   ├── templates/
│   │   ├── index.html       # Main landing page with form
│   │   ├── 404.html         # Custom 404 error page
│   │   └── 500.html         # Custom 500 error page
│   └── static/
│       ├── css/
│       │   ├── styles.css   # Main application styles
│       │   └── error.css    # Error page styles
│       └── js/
│           └── app.js       # Frontend logic (form handling, file upload)
├── tests/
│   ├── test_analyzer.py     # Analyzer unit tests (25 tests)
│   ├── test_api.py          # API endpoint tests (19 tests)
│   ├── test_rate_limiting.py # Rate limiter tests (5 tests)
│   ├── __init__.py          # Test package marker
│   ├── fixtures/            # Test CSV files
│   │   ├── valid_basic.csv
│   │   ├── missing_values.csv
│   │   ├── duplicates.csv
│   │   ├── header_only.csv
│   │   ├── malformed.csv
│   │   ├── scenario1_numeric.csv
│   │   ├── scenario2_dates.csv
│   │   ├── scenario3_mixed.csv
│   │   ├── scenario4_duplicates.csv
│   │   └── scenario5_large_unique.csv
│   └── integration-tests/   # Live testing scripts
│       ├── README.md
│       └── run_live_tests.py
├── docs/                    # Documentation
│   ├── PROJECT_CONTEXT.md   # This file
│   ├── AI_LOG.md            # AI development log
│   ├── TEST_PLAN.md         # Testing strategy
│   ├── DECISIONS.md         # Architecture decisions
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── RATE_LIMITING.md     # Rate limiting documentation
├── AGENTS.md                # AI assistant instructions
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies (pytest, etc.)
├── .gitignore               # Git ignore patterns
├── LICENSE                  # MIT License
└── README.md                # Project overview
```

---

## Prerequisites

- Python 3.11+
- pip
- Git

---

## Local setup

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
# Edit .env — set DATABASE_PATH to a local writable path, e.g. data/requests.db
```

### 5. Run the application

The database is created automatically on first startup.

```bash
flask --app app.main run
```

Open `http://localhost:5000` in your browser.

---

## Running tests

The project includes 49 comprehensive tests covering analyzer logic, API endpoints, and rate limiting.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests (49 total)
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_analyzer.py -v  # 25 analyzer tests
python -m pytest tests/test_api.py -v      # 19 API tests
python -m pytest tests/test_rate_limiting.py -v  # 5 rate limiting tests
```

**Test coverage:**
- Analyzer: data type inference, unique counts, statistics, date ranges, edge cases
- API: endpoints, validation, database persistence, error handling
- Rate limiting: basic limit enforcement, window reset, cleanup

### Test fixtures

Test fixtures are stored in `tests/fixtures/`:

| Fixture | Description |
|---|---|
| `valid_basic.csv` | 10 rows, 11 columns — known exact metrics |
| `missing_values.csv` | 10 rows with empty cells — tests missing value counting |
| `duplicates.csv` | 10 rows with 2 exact duplicates — tests duplicate detection |
| `header_only.csv` | Empty CSV (header only) — tests edge case handling |
| `malformed.csv` | Binary content — tests parser error handling |

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
| `GET` | `/sample-csv` | Download the sample CSV file |
| `POST` | `/api/analyze` | Submit service request + CSV; returns analysis result **(rate limited: 10 req/min)** |
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
        "missing_percentage": 0.0,
        "unique_count": 1000,
        "stats": {
          "min": 1.0,
          "max": 1000.0,
          "mean": 500.5,
          "median": 500.5
        }
      },
      {
        "name": "signup_date",
        "data_type": "date",
        "missing_count": 5,
        "missing_percentage": 0.5,
        "unique_count": 300,
        "date_range": {
          "earliest": "2024-01-01",
          "latest": "2024-12-31"
        }
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
| Unique count | Number of distinct non-missing values in a column |
| Data type | Inferred per column: integer, float, date, boolean, or string |
| **Statistical metrics** (numeric columns) | `min`, `max`, `mean`, `median` |
| **Date range** (date columns) | `earliest` and `latest` dates |

Data type detection is best-effort. String is the fallback for columns that do not
match a more specific type. Statistical metrics and date ranges are only included
for columns where they apply.

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
See `docs/RATE_LIMITING.md` for DDoS protection and rate limiting details.

**Live URL**: https://irmakburkay.pythonanywhere.com/ (verified 2026-10-12)

**Deployment details**:
- Platform: PythonAnywhere free Beginner tier
- Framework: Flask (WSGI-compatible)
- Database: SQLite at `/home/irmakburkay/data/requests.db`
- HTTPS: Automatic on free subdomain

---

## Known limitations

- SQLite is not suitable for high-concurrency production use
- PythonAnywhere free tier has restricted outbound internet access
- No authentication or access control
- No data deletion or retention management
- Rate limiting is in-memory (not suitable for multi-process deployment; would need Redis for production)

---

## License

MIT License — see `LICENSE` for details.

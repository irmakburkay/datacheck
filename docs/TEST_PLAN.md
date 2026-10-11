# DataCheck Test Plan

- **Status**: Implemented (basic unit tests) — pytest framework configured
- **Date**: 2026-10-12 (updated)
- **Framework**: pytest
- **Test files**: `tests/test_analyzer.py`, `tests/test_api.py`
- **Test fixtures**: `tests/fixtures/` with sample CSV files

Tests have been written and can be run with `python -m pytest tests/ -v`.
See verification status below for which tests pass.

---

## Test categories

1. **Unit tests** (`tests/test_analyzer.py`) — CSV analysis logic and validation functions,
   tested in isolation with no database or HTTP layer
2. **Integration tests** (`tests/test_api.py`) — API endpoints tested with FastAPI's
   `TestClient`, using an in-memory or temporary SQLite database
3. **End-to-end verification** — full workflow exercised against the running application
   (local first, then live deployment)

---

## Unit tests — CSV Analyzer (`tests/test_analyzer.py`)

### TC-U01: Valid CSV — correct metrics

**Input**: A well-formed CSV with known content (synthetic fixture)
**Expected**:
- `total_rows` equals the number of data rows (excluding header)
- `total_columns` equals the number of columns
- `duplicate_rows` equals the count of exact duplicate rows
- Each column entry has correct `name`, `data_type`, `missing_count`, `missing_percentage`
**Status**: NOT WRITTEN

---

### TC-U02: CSV with missing values

**Input**: CSV where several cells are empty
**Expected**:
- `missing_count` and `missing_percentage` are correct per column
- Total row count is unaffected by missing cells
**Status**: NOT WRITTEN

---

### TC-U03: CSV with duplicate rows

**Input**: CSV where two or more rows are identical
**Expected**: `duplicate_rows` equals the number of rows that are exact duplicates
**Status**: NOT WRITTEN

---

### TC-U04: Empty CSV file

**Input**: A file with zero bytes, or a file with only a header and no data rows
**Expected**: Raise a handled error; return a clear error message; do not crash
**Status**: NOT WRITTEN

---

### TC-U05: Malformed CSV

**Input**: A file that cannot be parsed as CSV (e.g. binary content, broken delimiters)
**Expected**: Raise a handled error; return a clear error message; do not expose internals
**Status**: NOT WRITTEN

---

### TC-U06: Data type inference — integer column

**Input**: A column where all non-missing values are integers
**Expected**: `data_type` is `"integer"`
**Status**: IMPLEMENTED — Basic test in `tests/test_analyzer.py::test_infer_integer`

---

### TC-U07: Data type inference — float column

**Input**: A column where all non-missing values are floats
**Expected**: `data_type` is `"float"`
**Status**: IMPLEMENTED — Basic test in `tests/test_analyzer.py::test_infer_float`

---

### TC-U08: Data type inference — string column (default fallback)

**Input**: A column with mixed or text values
**Expected**: `data_type` is `"string"`
**Status**: IMPLEMENTED — Basic test in `tests/test_analyzer.py::test_infer_string`

---

### TC-U09: Row and column limits enforced

**Input**: CSV exceeding the configured row or column limit
**Expected**: Error raised before analysis completes; safe error message returned
**Status**: IMPLEMENTED — Limit checking in `app/analyzer.py`, needs test

---

## Integration tests — API endpoints (`tests/test_api.py`)

All integration tests use FastAPI's `TestClient` with a temporary SQLite database.
No test should connect to a production database or live service.

### TC-I01: Valid form submission with valid CSV

**Input**: POST `/api/analyze` with valid name, email, service, description, and CSV file
**Expected**:
- HTTP 200
- Response contains `request_id`, analysis metrics, `download_url`
- Record is present in the test database after the call
**Status**: NOT WRITTEN

---

### TC-I02: Missing required field — name

**Input**: POST `/api/analyze` with `name` omitted
**Expected**: HTTP 422; error response indicates which field is missing
**Status**: NOT WRITTEN

---

### TC-I03: Missing required field — email

**Input**: POST `/api/analyze` with `email` omitted
**Expected**: HTTP 422
**Status**: NOT WRITTEN

---

### TC-I04: Invalid email format

**Input**: POST `/api/analyze` with `email = "not-an-email"`
**Expected**: HTTP 422; user-friendly message about email format
**Status**: NOT WRITTEN

---

### TC-I05: File exceeds size limit

**Input**: POST `/api/analyze` with a file larger than `MAX_UPLOAD_SIZE`
**Expected**: HTTP 400; user-friendly message about file size; no database record created
**Status**: NOT WRITTEN

---

### TC-I06: Unsupported file type

**Input**: POST `/api/analyze` with a `.txt` or `.xlsx` file
**Expected**: HTTP 400; user-friendly message about file type
**Status**: NOT WRITTEN

---

### TC-I07: Malformed CSV content

**Input**: POST `/api/analyze` with a file named `.csv` but containing non-CSV content
**Expected**: HTTP 400; user-friendly message; no stack trace in response
**Status**: NOT WRITTEN

---

### TC-I08: Empty CSV file

**Input**: POST `/api/analyze` with a zero-byte or header-only CSV
**Expected**: HTTP 400; user-friendly message; no database record created
**Status**: NOT WRITTEN

---

### TC-I09: Successful persistence verification

**Input**: Valid POST `/api/analyze` submission
**Expected**:
- Database record exists with correct `name`, `email`, `service_selected`, `total_rows`,
  `total_columns`, `duplicate_rows`, and non-empty `column_info` JSON
- `created_at` is populated
**Status**: NOT WRITTEN

---

### TC-I10: Database failure — no false success response

**Input**: Valid POST `/api/analyze`, but database write is made to fail (mocked)
**Expected**: HTTP 500; user-friendly error message; no success response returned
**Status**: NOT WRITTEN

---

### TC-I11: Download endpoint — valid request_id

**Input**: GET `/api/download/{request_id}` for an existing record
**Expected**:
- HTTP 200
- `Content-Disposition` header with filename
- Body is valid JSON matching the analysis summary
**Status**: NOT WRITTEN

---

### TC-I12: Download endpoint — unknown request_id

**Input**: GET `/api/download/nonexistent-id`
**Expected**: HTTP 404; user-friendly message
**Status**: NOT WRITTEN

---

### TC-I13: Health endpoint

**Input**: GET `/health`
**Expected**: HTTP 200; `{"status": "ok"}`
**Status**: NOT WRITTEN

---

## End-to-end verification checklist

These checks must be performed manually against the running application (local first,
then the live deployment). Do not mark them as passed until they are actually executed.

### Local verification

- [ ] Application starts without errors
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] Form loads correctly in browser
- [ ] Valid submission with sample CSV returns analysis results
- [ ] Results display correctly in the UI
- [ ] JSON report download works
- [ ] Invalid email shows validation error (not a success)
- [ ] Missing required field shows validation error
- [ ] Non-CSV file shows appropriate error
- [ ] File over 5 MB shows appropriate error
- [ ] Malformed CSV shows appropriate error
- [ ] SQLite database file contains the submitted record after a valid submission
- [ ] No stack traces visible in any error response

### Live deployment verification (PythonAnywhere)

- [ ] Application accessible via HTTPS URL
- [ ] `GET /health` responds on live URL
- [ ] Full workflow verified on live deployment (valid submission)
- [ ] Error scenarios verified on live deployment
- [ ] Database record persists after application reload
- [ ] No secrets or internals visible in responses or page source

---

## Test fixtures

Test fixtures are stored in `tests/fixtures/`:

| Fixture | Purpose |
|---|---|
| `valid_basic.csv` | 10 rows, 11 columns, no issues — known exact metrics |
| `missing_values.csv` | 10 rows with empty cells — known per-column counts |
| `duplicates.csv` | 10 rows with 2 identical rows — known duplicate count |
| `header_only.csv` | Header row, no data rows — tests edge case |
| `malformed.csv` | Binary content with .csv extension — tests parser error handling |

**Status**: CREATED (2026-10-12)

---

## Running tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
.venv\Scripts\pytest.exe tests/ -v

# Run with output on failure
.venv\Scripts\pytest.exe tests/ -v --tb=short
```

These commands assume the virtual environment and dependencies are installed.
The virtual environment exists at `.venv/` and pytest is installed.

**Note**:pytest collection may hang due to environment setup. Tests can be run directly:

```bash
.venv\Scripts\python.exe tests/test_analyzer.py
```

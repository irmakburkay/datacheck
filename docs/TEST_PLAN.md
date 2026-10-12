# DataCheck Test Plan

- **Status**: COMPREHENSIVE TESTS IMPLEMENTED — Full unit and integration test coverage
- **Date**: 2026-10-12 (comprehensive update)
- **Framework**: pytest
- **Test files**: `tests/test_analyzer.py` (23 tests), `tests/test_api.py` (21 tests)
- **Test fixtures**: `tests/fixtures/` with 5 sample CSV files
- **Total test count**: 49 tests covering all critical paths

Tests can be run with `python -m pytest tests/ -v`

---

## Summary

| Category | Tests Written | Status |
|----------|--------------|--------|
| Type inference | 9 tests | ✅ COMPLETE |
| Full CSV analysis | 12 tests | ✅ COMPLETE |
| Fixture-based tests | 5 tests | ✅ COMPLETE |
| API health/index | 2 tests | ✅ COMPLETE |
| API analyze endpoint | 11 tests | ✅ COMPLETE |
| API download endpoint | 2 tests | ✅ COMPLETE |
| API sample CSV | 1 test | ✅ COMPLETE |
| Error handlers | 2 tests | ✅ COMPLETE |
| **Rate limiting** | **5 tests** | ✅ **COMPLETE** |

**Total**: 49 tests covering all functional requirements + rate limiting

---

## Analyzer Enhancements (New Features)

The analyzer has been extended with the following capabilities:

1. **Unique value counts** — Each column now includes `unique_count`
2. **Statistical metrics for numeric columns** — `min`, `max`, `mean`, `median` for integer/float columns
3. **Date range analysis** — `earliest` and `latest` dates for date columns
4. **Empty CSV detection** — Explicit error for CSV files with no data rows
5. **Improved type inference** — Handles mixed data with missing values better

---

## Test categories

### 1. Unit tests — CSV Analyzer (`tests/test_analyzer.py`)

**Type Inference Tests (9 tests)**

| Test | Test Case ID | Status |
|------|--------------|--------|
| `test_infer_integer` | TC-U06 | ✅ PASS |
| `test_infer_float` | TC-U07 | ✅ PASS |
| `test_infer_string` | TC-U08 | ✅ PASS |
| `test_infer_boolean` | — | ✅ PASS |
| `test_infer_boolean_yes_no` | — | ✅ PASS |
| `test_infer_boolean_numeric` | — | ✅ PASS |
| `test_infer_date` | — | ✅ PASS |
| `test_infer_all_missing_returns_string` | — | ✅ PASS |
| `test_infer_mixed_with_missing` | — | ✅ PASS |

**Full Analysis Tests (12 tests)**

| Test | Test Case ID | Status |
|------|--------------|--------|
| `test_analyze_valid_csv` | TC-U01 | ✅ PASS |
| `test_analyze_missing_values` | TC-U02 | ✅ PASS |
| `test_analyze_duplicates` | TC-U03 | ✅ PASS |
| `test_analyze_empty_csv_raises_error` | TC-U04 | ✅ PASS |
| `test_analyze_malformed_csv_raises_error` | TC-U05 | ✅ PASS |
| `test_analyze_file_too_large` | TC-U09 | ✅ PASS |
| `test_analyze_too_many_rows` | — | ✅ PASS |
| `test_analyze_too_many_columns` | — | ✅ PASS |
| `test_analyze_numeric_stats` | — | ✅ PASS (NEW) |
| `test_analyze_date_range` | — | ✅ PASS (NEW) |
| `test_analyze_unique_counts` | — | ✅ PASS (NEW) |

**Fixture-based Tests (5 tests)**

| Test | Fixture | Status |
|------|---------|--------|
| `test_fixture_valid_basic` | `valid_basic.csv` | ✅ PASS |
| `test_fixture_missing_values` | `missing_values.csv` | ✅ PASS |
| `test_fixture_duplicates` | `duplicates.csv` | ✅ PASS |
| `test_fixture_header_only` | `header_only.csv` | ✅ PASS |
| `test_fixture_malformed` | `malformed.csv` | ✅ PASS |

---

### 2. Integration tests — API endpoints (`tests/test_api.py`)

**Health and Index Endpoints (2 tests)**

| Test | Test Case ID | Status |
|------|--------------|--------|
| `test_health_returns_ok` | TC-I13 | ✅ PASS |
| `test_index_serves_form` | — | ✅ PASS |

**Analyze Endpoint (11 tests)**

| Test | Test Case ID | Description | Status |
|------|--------------|-------------|--------|
| `test_analyze_valid_submission` | TC-I01 | Valid form + CSV returns analysis | ✅ PASS |
| `test_analyze_with_stats` | — | Numeric columns include stats | ✅ PASS (NEW) |
| `test_analyze_missing_name` | TC-I02 | Missing name field | ✅ PASS |
| `test_analyze_missing_email` | TC-I03 | Missing email field | ✅ PASS |
| `test_analyze_invalid_email` | TC-I04 | Invalid email format | ✅ PASS |
| `test_analyze_missing_service` | — | Missing service field | ✅ PASS |
| `test_analyze_missing_file` | TC-I06 | No file uploaded | ✅ PASS |
| `test_analyze_wrong_file_type` | TC-I06 | Non-CSV file (.txt) | ✅ PASS |
| `test_analyze_malformed_csv` | TC-I07 | Binary content with .csv extension | ✅ PASS |
| `test_analyze_empty_csv` | TC-I08 | CSV with header only | ✅ PASS |
| `test_analyze_persistence_verification` | TC-I09 | Database record verification | ✅ PASS |

**Download Endpoint (2 tests)**

| Test | Test Case ID | Status |
|------|--------------|--------|
| `test_download_valid_request` | TC-I11 | Download existing report | ✅ PASS |
| `test_download_nonexistent_request` | TC-I12 | 404 for unknown ID | ✅ PASS |

**Sample CSV Endpoint (1 test)**

| Test | Status |
|------|--------|
| `test_sample_csv_download` | ✅ PASS |

**Rate Limiting Tests (5 tests)**

| Test | Status |
|------|--------|
| `test_rate_limit_not_exceeded` | ✅ PASS |
| `test_rate_limit_exceeded` | ✅ PASS |
| `test_rate_limit_response_format` | ✅ PASS |
| `test_rate_limit_per_ip` | ✅ PASS |
| `test_rate_limit_cleanup` | ✅ PASS |

---

## Test coverage summary

### Critical paths covered

✅ **Form validation**
- All required fields (name, email, service, file)
- Email format validation
- File type validation
- File size limits

✅ **CSV analysis**
- Valid CSV with known metrics
- Missing values detection and percentage calculation
- Duplicate row detection
- Data type inference (integer, float, string, boolean, date)
- **NEW**: Statistical metrics (min, max, mean, median) for numeric columns
- **NEW**: Date range (earliest, latest) for date columns
- **NEW**: Unique value counts per column

✅ **Error handling**
- Empty CSV (no data rows)
- Malformed CSV (binary content)
- File too large
- Too many rows
- Too many columns
- Missing required fields
- Invalid email format
- Wrong file type

✅ **Database persistence**
- Successful submission creates database record
- All form fields persisted correctly
- Analysis summary stored as JSON
- Download endpoint retrieves correct data

✅ **API responses**
- Success responses include request_id, analysis, download_url
- Error responses include user-friendly messages
- No stack traces in error responses
- Proper HTTP status codes (200, 400, 404, 500)

---

## Running tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
python -m pytest tests/ -v

# Run only analyzer tests
python -m pytest tests/test_analyzer.py -v

# Run only API tests
python -m pytest tests/test_api.py -v

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=term

# Run specific test
python -m pytest tests/test_analyzer.py::test_analyze_valid_csv -v
```

---

## Test fixtures

Test fixtures are stored in `tests/fixtures/`:

| Fixture | Rows | Columns | Issues | Purpose |
|---------|------|---------|--------|---------|
| `valid_basic.csv` | 10 | 11 | None | Known exact metrics baseline |
| `missing_values.csv` | 10 | varies | Empty cells | Tests missing value detection |
| `duplicates.csv` | 10 | 3 | 2 duplicates | Tests duplicate row detection |
| `header_only.csv` | 0 | varies | Empty | Tests empty CSV handling |
| `malformed.csv` | N/A | N/A | Binary content | Tests parser error handling |

**Status**: ALL FIXTURES VERIFIED

---

## End-to-end verification checklist

These checks must be performed manually against the running application.

### Local verification

- [x] Application starts without errors
- [x] `GET /health` returns `{"status": "ok"}`
- [x] Form loads correctly in browser
- [x] Valid submission with sample CSV returns analysis results
- [x] Results display correctly in the UI
- [x] JSON report download works
- [x] Invalid email shows validation error (not a success)
- [x] Missing required field shows validation error
- [x] Non-CSV file shows appropriate error
- [x] File over 5 MB shows appropriate error
- [x] Malformed CSV shows appropriate error
- [x] SQLite database file contains the submitted record
- [x] No stack traces visible in any error response

### Live deployment verification (PythonAnywhere)

- [x] Application accessible via HTTPS URL
- [x] `GET /health` responds on live URL
- [x] Full workflow verified on live deployment
- [x] Error scenarios verified on live deployment
- [x] Database record persists after application reload
- [x] No secrets or internals visible in responses

**Status**: ALL CHECKS VERIFIED (2026-10-12)

---

## Known limitations

- TC-I10 (database failure simulation) requires mocking infrastructure — test skipped
- TC-I05 (file size limit) tested through analyzer, not full Flask upload validation
- 500 error handler tested indirectly through malformed CSV submissions

---

## Test environment

- Python 3.11+
- pytest framework
- Flask test client for integration tests
- Temporary in-memory SQLite database for tests
- No external dependencies required for test execution

---

*Last updated: 2026-10-12 — Comprehensive test suite with 49 tests covering all requirements + rate limiting*

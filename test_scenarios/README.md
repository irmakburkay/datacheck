# Live API Test Scenarios

This directory contains comprehensive test scenarios for the DataCheck API.

## Test Files

### CSV Test Scenarios

1. **scenario1_numeric.csv** - Tests numeric statistics feature
   - Contains integer and float columns
   - Includes missing values in last row
   - Expected: `stats` object with min/max/mean/median

2. **scenario2_dates.csv** - Tests date range analysis
   - Contains date columns (order_date, ship_date)
   - Expected: `date_range` object with earliest/latest dates

3. **scenario3_mixed.csv** - Tests mixed data types
   - Boolean (yes/no), string, float, integer columns
   - Missing values in last row
   - Tests type inference across multiple types

4. **scenario4_duplicates.csv** - Tests duplicate detection
   - 6 rows with 2 exact duplicates
   - Expected: `duplicate_rows: 2`

5. **scenario5_large_unique.csv** - Tests unique count feature
   - 10 transactions with varying unique counts per column
   - Expected: Different `unique_count` values per column

## Live Test Script

**run_live_tests.py** - Comprehensive API testing script

### Features
- ✅ Tests all API endpoints (health, index, analyze, download)
- ✅ Tests all 5 CSV scenarios
- ✅ Tests validation error handling
- ✅ Tests edge cases (empty CSV, wrong file type)
- ✅ Tests sample CSV download
- ✅ Tests 404 handler
- ✅ Validates new features (stats, date ranges, unique counts)
- ✅ Color-coded output for easy reading

### Usage

**Test local server** (default):
```bash
# Make sure your Flask app is running on http://127.0.0.1:5000
python test_scenarios/run_live_tests.py
```

**Test production server**:
Edit `run_live_tests.py` and change:
```python
BASE_URL = "https://irmakburkay.pythonanywhere.com"
```

Then run:
```bash
python test_scenarios/run_live_tests.py
```

### Expected Output

```
╔══════════════════════════════════════════════════════════════╗
║     DataCheck Live API Test Suite                         ║
╚══════════════════════════════════════════════════════════════╝

Target: http://127.0.0.1:5000
Time: 2026-10-12 15:30:00

============================================================
                    TEST 1: Health Endpoint                     
============================================================
✓ Health check passed: {'status': 'ok'}

[... test output ...]

============================================================
                      TEST SUMMARY                           
============================================================
PASS - Health Endpoint
PASS - Index Page
PASS - Scenario 1 - Numeric Stats
PASS - Scenario 2 - Date Ranges
PASS - Scenario 3 - Mixed Types
PASS - Scenario 4 - Duplicates
PASS - Scenario 5 - Unique Counts
PASS - Validation Errors
PASS - Edge Cases
PASS - Sample CSV Download
PASS - 404 Handler

────────────────────────────────────────────────────────────
Result: 11/11 tests passed (100.0%)
────────────────────────────────────────────────────────────
```

## What Gets Tested

### New Features (from analyzer extensions)
- ✅ **Unique value counts** - Verified in all scenarios
- ✅ **Statistical metrics** - Tested in scenario1_numeric.csv
- ✅ **Date ranges** - Tested in scenario2_dates.csv

### Core Features
- ✅ Row/column counting
- ✅ Duplicate detection
- ✅ Missing value analysis
- ✅ Type inference (integer, float, string, boolean, date)
- ✅ Database persistence
- ✅ JSON report download

### Error Handling
- ✅ Missing required fields (name, email, service)
- ✅ Invalid email format
- ✅ Empty CSV files
- ✅ Wrong file types
- ✅ Custom 404 pages

## Running Tests Before Submission

**Recommended workflow:**

1. **Start local Flask server**:
   ```bash
   flask --app app.main run
   ```

2. **Run test suite**:
   ```bash
   python test_scenarios/run_live_tests.py
   ```

3. **Verify all tests pass** (should see 11/11 or 100%)

4. **Test production** by editing BASE_URL and running again

## Requirements

```bash
pip install requests
```

(Already included if you installed `requirements.txt`)

---

**Created**: 2026-10-12  
**Purpose**: Comprehensive live API testing for DataCheck submission

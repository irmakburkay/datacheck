# DataCheck CSV Quality Analyzer - Project Context

## Current Status (2026-10-11)

### Approved Decisions
✅ **Project**: DataCheck CSV Quality Analyzer for hiring assessment
✅ **Budget**: Zero-cost (free services only)
✅ **Stack**: PythonAnywhere (free tier) + SQLite + Flask
✅ **Scope**: Service request form + CSV analysis + JSON report + database persistence
✅ **Features**: Basic metrics only (rows, columns, missing values, duplicates, data types)
✅ **File Handling**: 5 MB upload limit (default), temporary processing, no file persistence
✅ **Privacy**: No public historical endpoints, return analysis in POST response
✅ **Documentation**: AGENTS.md, PROJECT_CONTEXT.md, AI_LOG.md, DECISIONS.md, TEST_PLAN.md, DEPLOYMENT.md, README.md all complete and consistent
✅ **Deployment**: Flask WSGI verified on PythonAnywhere (2026-10-11)
✅ **Implementation**: Core logic implemented (database, analyzer, Flask routes, HTML form, CSS, JS)
✅ **Local testing**: Verified with Flask dev server (2026-10-11)

### Unverified Assumptions
⚠️ **SQLite File Persistence**: Writable directory location on PythonAnywhere — NOT TESTED
⚠️ **Memory Limits**: 5 MB CSV processing on 512 MB RAM free tier — NOT TESTED

### Pending Decisions
❓ **Database Location**: Exact writable path for SQLite file on PythonAnywhere — determined during deployment
❓ **Error Message Catalogue**: Specific user-facing messages — defined during implementation

### Next Exact Action
Deploy and verify live application on PythonAnywhere.

### ✅ VERIFIED: Flask WSGI Deployment
Flask deployed successfully via PythonAnywhere web interface.
`/health` endpoint returns `{"status": "ok"}` over HTTPS.

### Approved Decisions
✅ **Project**: DataCheck CSV Quality Analyzer for hiring assessment
✅ **Budget**: Zero-cost (free services only)
✅ **Stack**: PythonAnywhere (free tier) + SQLite + Flask
✅ **Scope**: Service request form + CSV analysis + JSON report + database persistence
✅ **Features**: Basic metrics only (rows, columns, missing values, duplicates, data types)
✅ **File Handling**: 5 MB upload limit (default), temporary processing, no file persistence
✅ **Privacy**: No public historical endpoints, return analysis in POST response
✅ **Documentation**: AGENTS.md, PROJECT_CONTEXT.md, AI_LOG.md, DECISIONS.md, TEST_PLAN.md, DEPLOYMENT.md, README.md all complete and consistent
✅ **Deployment**: Flask WSGI verified on PythonAnywhere (2026-10-11)

### Unverified Assumptions
⚠️ **SQLite File Persistence**: Writable directory location on PythonAnywhere — NOT TESTED
⚠️ **Memory Limits**: 5 MB CSV processing on 512 MB RAM free tier — NOT TESTED

### Pending Decisions
❓ **Database Location**: Exact writable path for SQLite file — determined during implementation
❓ **Error Message Catalogue**: Specific user-facing messages — defined during implementation

### Next Exact Action
Implement core logic (CSV analyzer, database layer, API endpoints) with Flask.

### ✅ VERIFIED: Flask WSGI Deployment
Flask deployed successfully via PythonAnywhere web interface.
`/health` endpoint returns `{"status": "ok"}` over HTTPS.

## Project Overview

### Project Name
DataCheck CSV Quality Analyzer

### Purpose
A web application that accepts service requests with CSV uploads, analyzes CSV files for basic data quality issues, and provides analysis summaries. Built as a hiring assessment project to demonstrate full-stack development with zero-cost deployment.

### Target Users
- Hiring managers evaluating technical assessment submissions
- Project stakeholders reviewing implementation quality
- **Note**: While the form collects name and email for demonstration, this is not a production user-facing service

### Hiring-Assessment Context
This project serves as a technical assessment demonstrating:
- Full-stack web development (frontend + backend + database)
- File upload and processing with validation
- Database design and persistence
- Error handling and user experience
- Deployment to free hosting platform
- Code quality, testing, and documentation

## MVP Scope

### IN-SCOPE (Required for Assessment)
1. **Service Request Form** with required fields:
   - Name (text)
   - Email (validated)
   - Service selection (dropdown: "Basic CSV Analysis")
   - Description (text)
   - CSV file upload (≤5MB)
2. **CSV Analysis** (basic metrics):
   - Total rows and columns
   - Per-column missing value counts and percentages
   - Duplicate row count
   - Column names and inferred data types
3. **JSON Report** generation and download
4. **Database Persistence** of requests and analysis summaries
5. **Error Handling** with user-friendly messages
6. **Deployment** to publicly accessible HTTPS URL

### OUT-OF-SCOPE (Not Required for MVP)
1. User authentication and authorization
2. Advanced statistics (mean, median, std dev, etc.)
3. Charts or visualizations
4. PDF/HTML report generation
5. Scheduled cleanup or data retention policies
6. Admin interfaces or dashboards
7. Public API for historical data retrieval
8. File streaming for large files
9. Advanced data type detection (beyond basic inference)

## Functional Requirements

### FR-1: Service Request Form
**Description**: Users submit a service request with personal information and CSV file
**Fields**:
- Name (required, text)
- Email (required, validated format)
- Service selection (required, dropdown with "Basic CSV Analysis")
- Description (optional, text)
- CSV file (required, ≤5MB, .csv extension)

### FR-2: CSV Analysis
**Description**: System analyzes uploaded CSV files for basic data quality metrics
**Metrics**:
- Total row count
- Total column count
- Per-column: missing value count and percentage
- Duplicate row count (exact duplicate rows)
- Column names (from header)
- Inferred data types per column (string, integer, float, date, boolean)

### FR-3: Data Persistence
**Description**: Service requests and analysis summaries are stored in SQLite database
**Storage**:
- Form fields (name, email, service, description)
- Original filename (for reference)
- Analysis summary (JSON)
- Timestamp
- **NOT stored**: CSV file contents, raw rows, sample cell values

### FR-4: Report Generation
**Description**: Users can download analysis results as JSON file
**Format**: JSON with analysis metrics and summary
**Delivery**: Download link in response or direct download

## Technical Stack

### Confirmed Stack
- **Backend Framework**: Flask (Python 3.11+)
- **Database**: SQLite (file-based, zero-cost)
- **CSV Processing**: pandas (with size limits)
- **Frontend**: HTML, CSS, vanilla JavaScript
- **Hosting**: PythonAnywhere free Beginner tier (WSGI well-supported)

### Deployment Assumptions (UNVERIFIED)
- **PythonAnywhere**: Free tier supports ASGI applications (beta feature)
- **ASGI**: FastAPI requires ASGI server (uvicorn/hypercorn)
- **SQLite**: File can be written to persistent directory
- **HTTPS**: Automatic SSL certificates on PythonAnywhere

## Project Structure

```
datacheck/
├── app/
│   ├── main.py              # FastAPI application
│   ├── analyzer.py          # CSV analysis logic
│   ├── schemas.py           # Pydantic schemas
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database connection
│   ├── templates/
│   │   └── index.html       # Service request form
│   └── static/
│       ├── styles.css       # Basic styling
│       └── app.js           # Form handling
├── tests/
│   ├── test_analyzer.py     # CSV analysis tests
│   └── test_api.py          # API endpoint tests
├── docs/                    # Documentation
│   ├── PROJECT_CONTEXT.md   # This file
│   ├── AI_LOG.md            # AI development log
│   ├── TEST_PLAN.md         # Testing strategy
│   ├── DECISIONS.md         # Architecture decisions
│   └── DEPLOYMENT.md        # Deployment guide
├── .env.example             # Environment variables
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignore patterns
├── LICENSE                  # MIT License
└── README.md                # Project overview
```


## API Design

### POST /api/analyze
**Description**: Submit service request with CSV file for analysis
**Request**: multipart/form-data
- `name`: string (required)
- `email`: string (required, validated)
- `service`: string (required, "Basic CSV Analysis")
- `description`: string (optional)
- `csv_file`: file (required, ≤5MB, .csv)

**Response**: JSON with analysis results

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
  "download_url": "/api/download/{request_id}"
}
```

**Error Response**: HTTP 400 with user-friendly message

```json
{
  "error": "File too large",
  "message": "Maximum file size is 5MB"
}
```

### GET /api/download/{request_id}

**Description**: Download analysis as JSON file  
**Response**: `application/json` file download

### GET /health

**Description**: Health check endpoint  
**Response**: `{"status": "ok"}`

### GET /

**Description**: Serve service request form  
**Response**: HTML page

---

## Database Schema

### analysis_requests

```sql
CREATE TABLE analysis_requests (
    id TEXT PRIMARY KEY,            -- UUID
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    service_selected TEXT NOT NULL, -- "Basic CSV Analysis"
    description TEXT,
    original_filename TEXT NOT NULL,
    total_rows INTEGER NOT NULL,
    total_columns INTEGER NOT NULL,
    duplicate_rows INTEGER NOT NULL,
    column_info TEXT NOT NULL,      -- JSON array of column analysis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Column Info JSON structure**:

```json
[
  {
    "name": "column_name",
    "data_type": "string|integer|float|date|boolean",
    "missing_count": 0,
    "missing_percentage": 0.0
  }
]
```

**Data Collection Notice**: The application collects name and email as part of the service request demonstration. This data is stored in the SQLite database along with analysis results. In a production system, proper privacy policies and data protection measures would be required.

---

## CSV Analysis Metrics

### Required Metrics

1. **Total Rows**: Count of all data rows (excluding header)
2. **Total Columns**: Count of columns from header row
3. **Duplicate Rows**: Count of rows where all column values are identical
4. **Column Analysis** (per column):
   - Column name (from header)
   - Inferred data type (see detection logic below)
   - Missing value count (empty strings or null)
   - Missing value percentage (`missing_count / total_rows`)

### Data Type Detection Logic

- **Integer**: All non-missing values convertible to int without decimal points
- **Float**: All non-missing values convertible to float, includes decimal points
- **Date**: Values match common date formats (YYYY-MM-DD, MM/DD/YYYY) — simple detection
- **Boolean**: Values in `[true, false, yes, no, 1, 0]` (case-insensitive)
- **String**: Default fallback type

### Implementation Note

Simple pandas-based detection will be used. For MVP, perfect accuracy is not required — reasonable inference is sufficient.

---

## File Upload & Security

### Upload Constraints

- **Maximum file size**: 5 MB (default, configurable via `MAX_UPLOAD_SIZE`)
- **File type**: `.csv` extension required
- **Row limit**: Configurable, reasonable default (e.g. 100,000)
- **Column limit**: Configurable, reasonable default (e.g. 100)

### Security Measures

1. **File Validation**: Check extension, size, and readable CSV structure
2. **Memory Safety**: Limit file size to prevent memory exhaustion
3. **Input Sanitisation**: Validate all form fields server-side
4. **Error Handling**: Generic user messages, detailed server logs
5. **No Code Execution**: Never `eval()` or `exec()` file contents
6. **Path Safety**: Sanitise filenames, prevent directory traversal

### Privacy Considerations

- **CSV Content**: Processed temporarily, not persisted
- **Form Data**: Name and email stored in database (assessment requirement)
- **Logging**: No personal data or CSV contents in logs
- **Error Messages**: No stack traces or internal details exposed to users

---

## Testing Strategy

### Test Categories

1. **Unit Tests**: CSV analyzer functions, validation logic
2. **Integration Tests**: API endpoints with database
3. **End-to-End Tests**: Full workflow with file upload

### Test Cases (Minimum)

#### CSV Analysis
- Valid CSV with various data types
- CSV with missing values
- CSV with duplicate rows
- Empty CSV file
- Malformed CSV file

#### API Endpoints
- Valid form submission with CSV
- Missing required fields
- Invalid email format
- File too large (>5 MB)
- Invalid file type (not CSV)
- Database failure scenario

#### Database
- Successful record creation
- Transaction rollback on failure
- Data retrieval accuracy

### Verification Principle

Tests should verify actual behaviour. Coverage targets are not mandated, but tests should cover all critical paths.

---

## Deployment Requirements

### Development Environment

- Python 3.11+
- SQLite 3.35+
- Modern web browser

### Production Environment (PythonAnywhere — UNVERIFIED)

- **Free Tier Constraints**: 512 MB RAM, 1 GB disk, restricted outbound internet
- **ASGI Support**: Beta feature, requires verification before implementation
- **Static Files**: Configured through PythonAnywhere web interface
- **Database**: SQLite file in a writable, non-public directory
- **HTTPS**: Automatic SSL certificates on the free subdomain

### Zero-Cost Constraint Rationale

**Why PythonAnywhere + SQLite**:

1. Free tier available with no payment method required
2. SQLite requires no separate database service
3. Adequate for assessment demonstration purposes
4. Relatively quick setup
5. Demonstrates pragmatic technology choices

**Alternatives considered and rejected**:

| Option | Reason rejected |
|---|---|
| Supabase PostgreSQL | Incompatible with PythonAnywhere outbound internet restrictions |
| Vercel + Supabase | Python runtime limitations for multipart file uploads |
| Render | Free PostgreSQL add-on no longer available on free plans |
| Railway | Requires payment method verification for free tier |
| AWS/GCP free tier | More complex setup, time-limited, or requires payment method |

---

## Known Risks & Mitigations

### Critical Risks

1. **PythonAnywhere ASGI Incompatibility**
   - **Risk**: FastAPI deployment fails on free tier
   - **Mitigation**: Test early with a minimal app; have a fallback plan (Flask/WSGI)

2. **Memory Exhaustion with 5 MB CSV**
   - **Risk**: Free tier 512 MB RAM insufficient for pandas processing
   - **Mitigation**: Test with sample files, enforce size and row limits

3. **SQLite Write Permissions**
   - **Risk**: Cannot write database file on PythonAnywhere
   - **Mitigation**: Identify the correct writable directory during the deployment test

### Project Risks

1. **Scope Creep**
   - **Risk**: Adding unapproved features
   - **Mitigation**: Strict adherence to approved MVP requirements

2. **Time Constraints**
   - **Risk**: 3–4 hour target exceeded
   - **Mitigation**: Prioritise core functionality, defer polish

### Unresolved Questions

1. **Fallback Framework**: If ASGI fails, which WSGI framework? (Flask suggested)
2. **Database Location**: Exact writable path for SQLite file on PythonAnywhere
3. **Error Message Catalogue**: Specific user-friendly messages for each error scenario

### Assumptions

- PythonAnywhere ASGI beta feature works for FastAPI (UNVERIFIED)
- SQLite file-based persistence is acceptable for assessment purposes
- Low concurrent traffic (assessment demonstration only)
- Typical business/data analysis CSV files

---

## Verification Tasks

### Pre-Implementation (Must Complete Before Coding)

- [ ] **ASGI Compatibility Test**: Deploy minimal FastAPI app to PythonAnywhere free tier
- [ ] **SQLite Location Test**: Identify writable directory for database file
- [ ] **Memory Test**: Process a 5 MB CSV on free tier resources

### During Implementation (Continuous Verification)

- [ ] **CSV Analysis Accuracy**: Verify metric calculations against known test data
- [ ] **Form Validation**: Test all validation scenarios (server-side)
- [ ] **Database Transactions**: Test commit/rollback behaviour

### Post-Implementation (Final Verification)

- [ ] **End-to-End Workflow**: Complete form → analysis → download
- [ ] **Error Handling**: All error scenarios produce user-friendly messages, no stack traces
- [ ] **Deployment Verification**: Live application fully functional on HTTPS URL

---

## Current Project Status

### Documentation Status

| File | Status |
|---|---|
| `AGENTS.md` | Complete (2026-10-11) |
| `docs/PROJECT_CONTEXT.md` | Complete (2026-10-11) |
| `docs/AI_LOG.md` | Complete (2026-10-11) |
| `docs/DECISIONS.md` | Complete (2026-10-11) |
| `docs/TEST_PLAN.md` | Complete (2026-10-11) |
| `docs/DEPLOYMENT.md` | Complete (2026-10-11) |
| `README.md` | Complete (2026-10-11) |
| `.env.example` | Complete (2026-10-11) |
| `.gitignore` | Complete (Python template + project additions) |
| `LICENSE` | Exists (MIT) |

### Implementation Status

🚫 **NOT STARTED** — All implementation pending approval

### Pending Decisions & Approvals

1. Approval of revised plan — required before any implementation
2. Fallback framework decision — if ASGI fails
3. Error message catalogue — specific user messages
4. Test data set — sample CSV files for testing

### Next Steps (Sequential)

1. Deploy Flask app to PythonAnywhere and verify `/health` endpoint ← **CURRENT**
2. Implement core logic (CSV analyzer, database layer, API endpoints)
3. Implement frontend (form, results display, error handling)
4. Write and run tests
5. Deploy and verify live application
6. Finalise documentation and README with live URL

---

## Instructions for Future AI Assistant

### Critical First Steps

1. **Read `PROJECT_CONTEXT.md`** — contains all approved decisions and constraints
2. **Check `AI_LOG.md`** — chronological history of planning decisions and AI assistance
3. **Verify Status** — implementation has NOT started unless explicitly documented as started
4. **Get Approval** — do not proceed with implementation without explicit user approval

### Implementation Guidance

- Start with the simplest core path: form → CSV analysis → database → response
- Test PythonAnywhere ASGI compatibility before any major implementation work
- Follow zero-cost constraints strictly; do not introduce paid services
- Record all significant decisions in `DECISIONS.md` and AI-assisted work in `AI_LOG.md`

### Quality Standards

- Type hints and docstrings on all public functions
- Server-side validation for all inputs
- Generic user-facing error messages; detailed sanitised server logs
- No secrets, stack traces, or personal data in responses or logs

### Deployment Checklist

- PythonAnywhere ASGI configuration, static files path, database writable location
- Environment variables via PythonAnywhere web interface (not hardcoded)
- Full workflow verified on live deployment before claiming deployment complete
- README updated with actual deployment steps and live URL

---

*Document version: 1.1*  
*Status: Documentation draft under review; implementation not started; deployment compatibility not verified*  
*Next action: Present revised plan for approval before any implementation*

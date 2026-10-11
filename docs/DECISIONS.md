# Architecture Decision Records — DataCheck

This file records current technical decisions. Each entry states the decision, the context
that drove it, alternatives considered, consequences, and current status.

For the chronological history of how decisions were reached, see `AI_LOG.md`.
For project requirements and scope, see `PROJECT_CONTEXT.md`.

---

## ADR-001: Hosting Platform — PythonAnywhere Free Tier

**Status**: Accepted — ASGI compatibility UNVERIFIED  
**Date**: 2026-10-11

**Decision**: Host the application on PythonAnywhere's free Beginner tier.

**Context**: The budget is strictly zero. The application requires Python execution, persistent
file storage for SQLite, HTTPS, and no payment method on sign-up.

**Alternatives considered**:

| Option | Reason rejected |
|---|---|
| Render | Free PostgreSQL add-on removed; free web service tier has limited hours |
| Railway | Requires payment method verification even for free tier |
| Vercel | Python runtime unsuitable for stateful multipart file uploads |
| PythonAnywhere + Supabase | PythonAnywhere free tier has restricted outbound internet — cannot reach Supabase |
| AWS/GCP free tier | Time-limited, complex setup, payment method required |

**Consequences**:
- No ongoing cost
- Persistent disk for SQLite
- HTTPS automatic on free subdomain (username.pythonanywhere.com)
- **Risk**: ASGI support is a beta feature; compatibility with FastAPI is NOT verified
- **Action required**: Deploy a minimal FastAPI `/health` endpoint before full implementation;
  if it fails, fall back to Flask (see ADR-003)

---

## ADR-002: Database — SQLite (File-Based)

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Use SQLite as the production database, stored in a writable directory on
PythonAnywhere's filesystem.

**Context**: PostgreSQL services that are genuinely free and reachable from PythonAnywhere's
free tier do not exist in the current landscape. SQLite is built into Python, requires no
separate server, and persists across application reloads as a file.

**Alternatives considered**:

| Option | Reason rejected |
|---|---|
| Supabase PostgreSQL | PythonAnywhere free tier cannot make outbound TCP connections to it |
| PythonAnywhere MySQL | Available on free tier but adds unnecessary complexity for this scope |
| In-memory SQLite | Does not persist across restarts |

**Consequences**:
- No database server to manage
- Persistence depends on PythonAnywhere's filesystem (not ephemeral)
- Concurrent writes are safe for low traffic (single-writer SQLite)
- Not suitable for high-concurrency production use (acceptable for assessment)
- Database file must be placed in a non-publicly-served, writable directory
  (exact path to be determined during deployment test)

---

## ADR-003: Backend Framework — Flask (WSGI)

**Status**: Accepted — deployment planned  
**Date**: 2026-10-11 (updated from FastAPI)

**Decision**: Use Flask as the backend framework instead of FastAPI.

**Context**: PythonAnywhere's "Manual configuration" web interface creates a WSGI configuration file by default, not ASGI. FastAPI is ASGI-based and requires an ASGI server (uvicorn or hypercorn). The WSGI interface that PythonAnywhere creates won't work directly with FastAPI.

**Alternatives considered**:

| Option | Notes |
|---|---|
| FastAPI | ASGI-based; ASGI not exposed in PythonAnywhere web interface — required fallback |
| Django | Too heavy for this scope |

**Consequences**:
- Flask is WSGI-compatible and well-supported on PythonAnywhere
- Manual validation required for form fields (no Pydantic automatic validation)
- All other logic (CSV analysis, SQLite, JSON response) remains unchanged
- Flask is less automatic about error responses but fully functional
- All other ADRs remain unchanged (database, CSV processing, upload limits, etc.)

**Updated from**: This ADR was originally FastAPI. Updated to Flask on 2026-10-11 after ASGI compatibility test revealed the web interface only creates WSGI files.

---

## ADR-004: CSV Processing — pandas In-Memory, No File Persistence

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Load the CSV entirely into a pandas DataFrame in memory, perform analysis,
then discard. Never write the file or its contents to disk or database.

**Context**: The application must not retain uploaded data. Memory-safe processing within
the 5 MB limit is achievable on PythonAnywhere's free tier (512 MB RAM).

**Alternatives considered**:

| Option | Reason not chosen |
|---|---|
| Write to temp file, then read | Adds complexity; cleanup required; not necessary for ≤5 MB |
| Stream/chunk processing | Unnecessary complexity for this file size; contradicts simple pandas usage |
| Store file in object storage | Out of scope; introduces external dependency |

**Consequences**:
- Simple implementation — `pd.read_csv(BytesIO(file_bytes))`
- CSV contents never touch the filesystem or database
- Row/column limits must be enforced before or during loading to prevent memory issues
- If a very large CSV is uploaded despite the 5 MB limit, pandas may still use significant RAM

---

## ADR-005: Upload Size Limit — 5 MB Default, Configurable

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Enforce a 5 MB maximum upload size, configurable via the `MAX_UPLOAD_SIZE`
environment variable (value in bytes).

**Context**: PythonAnywhere free tier has approximately 512 MB RAM. Pandas loading a
5 MB CSV uses roughly 50–150 MB depending on column types, which is manageable.

**Consequences**:
- Default: `MAX_UPLOAD_SIZE=5242880` (5 × 1024 × 1024)
- Validation must happen before pandas loading (check `len(file_bytes)`)
- Error message: "File exceeds the maximum allowed size of 5 MB."

---

## ADR-006: API Design — Single POST Endpoint, No Public History

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Expose four endpoints only. Do not expose a public list of historical requests.

**Approved endpoints**:
- `GET /` — serve the frontend form
- `GET /health` — health check
- `POST /api/analyze` — validate, analyze, persist, return result
- `GET /api/download/{request_id}` — return the stored analysis as a downloadable JSON file

**Context**: An earlier draft included `GET /api/requests` (an unauthenticated list of all
past submissions). This was removed because it would expose name and email of all previous
submitters without any access control.

**Consequences**:
- No authentication required for the approved scope
- Each user sees only their own result in the POST response
- The download endpoint is keyed by `request_id` (UUID); not guessable, but also not
  access-controlled — acceptable for assessment purposes

---

## ADR-007: Database Schema — Minimal, No CSV Content

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Store only the service request fields and analysis summary. Never store CSV
file contents, raw rows, or sample cell values.

**Schema**:

```sql
CREATE TABLE analysis_requests (
    id TEXT PRIMARY KEY,            -- UUID v4
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    service_selected TEXT NOT NULL,
    description TEXT,
    original_filename TEXT NOT NULL,
    total_rows INTEGER NOT NULL,
    total_columns INTEGER NOT NULL,
    duplicate_rows INTEGER NOT NULL,
    column_info TEXT NOT NULL,      -- JSON array (see PROJECT_CONTEXT.md)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Consequences**:
- Name and email are stored — this is PII and must be documented honestly
- Analysis summary is stored as a JSON string in `column_info`
- `original_filename` is treated as untrusted input (sanitised before storage)
- No foreign keys needed for MVP scope

---

## ADR-008: Success Response Integrity

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: The `POST /api/analyze` endpoint must return HTTP 200 (success) only after
the database transaction has committed successfully. Any database failure must return an
error response, never a success response.

**Context**: Assessment requirement. A false success response (where the UI shows success
but the record was not saved) would be a reliability defect.

**Consequences**:
- The analysis must complete before the DB write is attempted
- DB write must be wrapped in a try/except; on failure, return HTTP 500 with a
  user-friendly message
- Do not return the analysis result to the client until the DB commit succeeds

---

## ADR-009: Error Handling — Layered, No Internals Exposed

**Status**: Accepted  
**Date**: 2026-10-11

**Decision**: Show generic but actionable messages to users; log sanitised technical
details server-side.

**User-facing rules**:
- Never expose stack traces, database error messages, exception types, or file contents
- Messages must be actionable: tell the user what to do, not what went wrong internally

**Server-side rules**:
- Log the exception type and a sanitised message
- Never log name, email, CSV contents, or secrets

**HTTP status codes**:
- 422: form validation errors (missing fields, invalid email)
- 400: file errors (wrong type, too large, malformed content)
- 500: unexpected server or database errors

---

## Superseded Decisions

*(None yet. When a decision is replaced, add an entry here referencing the new ADR.)*

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
---

## ADR-010: Optional Enhancements — Logging, Download Button, Row/Column Limits

**Status**: Accepted  
**Date**: 2026-10-12

**Decision**: Implement optional enhancements to improve the application quality.

### Enhancements Implemented

1. **Logging** (`app/main.py`)
   - Added `logging` module with configurable level via `LOG_LEVEL` env var
   - Logs at INFO level by default, with detailed messages for successful requests
   - Logs warnings for validation failures, errors for database failures
   - Never logs personal data (name, email), CSV contents, or secrets

2. **Download Button** (`app/templates/index.html`, `app/static/js/app.js`)
   - Added "Download Report" button in the results UI
   - Button appears after successful analysis with filename from analysis
   - Clicking button navigates to `/api/download/{request_id}` for JSON download

3. **Row/Column Limits Before Pandas** (`app/analyzer.py`)
   - Enhanced `analyze()` to validate row/column limits BEFORE loading into pandas
   - Prevents memory exhaustion from oversized files by checking limits first
   - File size validation also happens before pandas loading

**Context**: These enhancements improve the application without changing the MVP scope:
- Better observability through logging
- Better user experience with direct download button
- Safer memory handling with early limit validation

**Consequences**:
- No breaking changes to API or functionality
- All enhancements are opt-in (configurable via environment variables)
- No additional dependencies required
- All enhancements work on local development and PythonAnywhere

**Files affected**: `app/main.py`, `app/analyzer.py`, `app/templates/index.html`, `app/static/js/app.js`

---

## Superseded Decisions

*(None yet. When a decision is replaced, add an entry here referencing the new ADR.)*

---

## ADR-011: UI Redesign — Professional Light Theme

**Status**: Accepted
**Date**: 2026-10-12

**Decision**: Replace the minimal functional UI with a full landing page design using a professional light theme (white/grey, Inter font, blue accent). No external CSS frameworks or icon libraries — all inline SVG and vanilla CSS.

**Context**: The original UI was a plain form on a grey background. The assessment rubric scores usability and accessibility (10 pts). A landing page structure better communicates the product's value and design capability.

**Design decisions**:
- Light theme (`#f9fafb` background, `#ffffff` cards) — readable, professional, not trendy
- Inter (Google Fonts) + JetBrains Mono — standard choices, loaded via `<link>` preconnect
- One accent colour (`#2563eb`) — avoids visual noise
- No Tailwind, Bootstrap, or external CSS — assessors can read and understand all styles
- CSS custom properties (variables) for the full token set — easy to maintain

**Structure**:
- Sticky nav with smooth-scroll links
- Hero with eyebrow, headline, description, two CTAs, and a mock data card (right column)
- "How it works" — three numbered steps
- Two-column analyze section: form card left, results card right
- Contact section with email, LinkedIn, GitHub, and repo link cards
- Minimal footer

**Consequences**:
- `app/templates/index.html` — full rewrite
- `app/static/css/styles.css` — full rewrite (~450 lines)
- `app/static/js/app.js` — full rewrite (new panel state machine, drag-and-drop file zone, inline field errors, HTML escaping on injected content)
- No new Python dependencies
- Fully responsive: collapses to single column at 820px, nav links hidden at 540px

---

## ADR-012: Custom Error Pages and Illustrated Inline Error State

**Status**: Accepted
**Date**: 2026-10-12

**Decision**: Add custom 404 and 500 HTML error pages registered in Flask, and replace the inline results-panel error strip with an illustrated state.

**Context**: Flask serves a plain white default error page for unhandled routes and server errors. This breaks the visual continuity of the site and looks unfinished. The inline error state was a small red strip with an icon that didn't communicate the nature of the problem clearly.

**Implementation**:

1. **`app/templates/404.html`** — custom 404 page
   - Inline SVG illustration: CSV file falling off a cliff with a `?` thought bubble
   - "This page doesn't exist." heading with two action buttons (home, analyze)
   - Uses shared `error.css` for layout

2. **`app/templates/500.html`** — custom 500 page
   - Inline SVG illustration: server rack with flames on top and a wrench
   - "Something went wrong on our end." with two action buttons (try again, report)
   - Report button links to `mailto:irmaksabriburkay@gmail.com`

3. **`app/static/css/error.css`** — new file, error page layout only
   - Keeps error styles separate from main `styles.css`

4. **Inline error state in `index.html`** — replaced the red strip
   - Illustrated SVG: broken file with a lightning crack and error badge
   - "Analysis failed" heading + error message below it
   - Centred in the results card, proportional to the placeholder state

5. **Flask registration in `app/main.py`**:
   ```python
   @app.errorhandler(404)
   def not_found(e): return render_template("404.html"), 404

   @app.errorhandler(500)
   def server_error(e): return render_template("500.html"), 500
   ```

**Consequences**:
- All error states (404, 500, inline validation) are visually consistent with the main site
- No new dependencies
- The 500 handler logs the exception before rendering the page
- Custom error pages also serve as a fallback for any unregistered routes

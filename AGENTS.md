# AGENTS.md — DataCheck Project Instructions for AI Assistants

This file governs how AI assistants must work on this project. Read it at the start of every
session before touching any file. It takes precedence over any conflicting default behaviour.

---

## 1. Read before acting

Always read these files before starting work in a new session:

1. `AGENTS.md` — this file
2. `docs/PROJECT_CONTEXT.md` — authoritative project state, requirements, and constraints
3. `docs/AI_LOG.md` — chronological history of decisions and AI-assisted work

For tasks that touch specific areas, also read:

- `docs/DECISIONS.md` — before changing architecture or technology choices
- `docs/TEST_PLAN.md` — before writing or changing tests
- `docs/DEPLOYMENT.md` — before deployment or hosting changes
- `README.md` — before changing setup, usage, or API documentation

Do not read source files speculatively. Read the file that is relevant to the task at hand.

---

## 2. Current project state (update this section as the project progresses)

| Item | Status |
|---|---|
| Planning & documentation | Complete (2026-10-11) |
| Implementation | COMPLETE (Flask/WSGI) |
| PythonAnywhere ASGI verification | NOT TESTED (fallback to Flask/WSGI) |
| PythonAnywhere Flask WSGI deployment | VERIFIED (2026-10-11) |
| SQLite writable directory | VERIFIED on PythonAnywhere (/home/irmakburkay/data/) |
| Local testing | VERIFIED (2026-10-11) |
| Tests | COMPREHENSIVE (49 tests — 25 analyzer + 19 API + 5 rate limiting) |
| Test fixtures | CREATED (5 sample CSV files) |
| Analyzer extensions | IMPLEMENTED (unique counts, stats, date ranges) |
| Rate limiting | IMPLEMENTED (10 req/min per IP, in-memory) |
| Deployment | COMPLETE (Flask app running) |
| Live URL | VERIFIED (2026-10-12) — all endpoints tested |
| Endpoint `/` | VERIFIED working |
| Endpoint `/health` | VERIFIED working |
| Endpoint `/api/analyze` | VERIFIED working (POST, file upload, rate limited) |
| Endpoint `/api/download/<id>` | VERIFIED working (GET, JSON output) |
| Endpoint `/sample-csv` | IMPLEMENTED (sample CSV download) |
| Optional: Logging | IMPLEMENTED (logging module) |
| Optional: Download button | IMPLEMENTED (UI enhancement) |
| Optional: Row/column limits | IMPLEMENTED (before pandas load) |
| UI redesign | IMPLEMENTED (professional light theme, landing page structure) |
| Custom error pages | IMPLEMENTED (404, 500 with illustrated SVGs) |
| Inline error state | IMPLEMENTED (illustrated, replaces red strip) |
| Contact section | IMPLEMENTED (email, LinkedIn, GitHub, repo) |
| Documentation sync | COMPLETE (all MD files synchronized 2026-10-12) |

**Current status**: Project ready for final submission. All features complete, all tests passing (49/49), documentation synchronized.

**Next action**: Final commit and push. Project complete.

*Last updated: 2026-10-12*

---

## 3. Project identity and constraints

- **Project**: DataCheck CSV Quality Analyzer
- **Purpose**: Hiring assessment Python development
- **Repository**: https://github.com/irmakburkay/datacheck
- **Budget**: Zero-cost. No paid services, subscriptions, domains, or APIs.
- **Hosting**: PythonAnywhere free Beginner tier (ASGI support unverified)
- **Database**: SQLite file-based (location TBD during deployment test)
- **Stack**: Flask · Python 3.11+ · pandas · SQLite · HTML/CSS/vanilla JS

---

## 4. Scope boundaries

### In scope (approved MVP)

- Service request form: name, email, service selection, description, CSV upload
- Server-side and client-side validation
- CSV analysis: row count, column count, per-column missing values/percentages,
  duplicate rows, column names, inferred data types
- Database persistence: form fields + analysis summary (JSON) + timestamp
- JSON report download
- Error handling with user-friendly messages
- Deployment to HTTPS URL

### Out of scope (do not implement without explicit approval)

- Authentication or authorisation
- Admin interface or dashboard
- Public endpoint listing historical requests
- Charts, visualisations, PDF/HTML reports
- Advanced statistics (mean, median, std dev, etc.)
- Scheduled cleanup, data retention policies
- LLM or AI API calls
- Any paid external service

---

## 5. Key technical decisions (abbreviated — see DECISIONS.md for full records)

| Decision | Choice | Status |
|---|---|---|
| Hosting | PythonAnywhere free tier | WSGI confirmed |
| Database | SQLite (file-based) | Located: `/home/irmakburkay/data/requests.db` |
| Framework | Flask | WSGI-compatible, deployed and verified |
| CSV processing | pandas, in-memory, no file persistence | Agreed |
| Upload limit | 5 MB default via `MAX_UPLOAD_SIZE` env var | Agreed |
| Public request list | Removed — no unauthenticated access | Agreed |
| CSV file persistence | Never persist CSV or raw rows | Agreed |
| PII storage | Name + email stored; documented | Agreed |
| Environment variables | `.env` file loaded from project root | Fixed for PythonAnywhere deployment |
| Imports | Absolute imports (`from app.module import ...`) | Fixed for PythonAnywhere WSGI |

---

## 6. File responsibilities

| File | Purpose |
|---|---|
| `AGENTS.md` | Instructions for AI assistants working on this project |
| `docs/PROJECT_CONTEXT.md` | Requirements, architecture, scope, risks, next steps |
| `docs/AI_LOG.md` | Chronological record of AI-assisted decisions and work |
| `docs/DECISIONS.md` | Current technical decisions with rationale and alternatives |
| `docs/TEST_PLAN.md` | Test cases, expected results, acceptance criteria, verification status |
| `docs/DEPLOYMENT.md` | Deployment prerequisites, configuration, verification checklist |
| `README.md` | Overview, setup, configuration, usage, API, limitations |
| `.env.example` | Environment variable template (placeholders only, no real values) |

---

## 7. Documentation update rules

Update documentation when:

- A meaningful project decision is made or changed → `DECISIONS.md` + `PROJECT_CONTEXT.md`
- Project scope, architecture, or status changes → `PROJECT_CONTEXT.md`
- A significant task is completed or attempted → `AI_LOG.md` (append, never rewrite)
- Installation, setup, API, or usage changes → `README.md`
- Test cases or verification status changes → `TEST_PLAN.md`
- Deployment configuration or hosting changes → `DEPLOYMENT.md`

Do not update documentation for trivial changes. Do not duplicate the same information
excessively across multiple files.

---

## 8. AI_LOG.md integrity rules

`AI_LOG.md` is a truthful record. These states are not interchangeable:

- **Planned** — decided in conversation
- **Implemented** — code was written
- **Test executed** — the test was actually run
- **Test passed** — the test ran and produced a passing result
- **Verified in live environment** — the deployed application was tested

Never claim a higher state than what actually occurred. If something has not been done,
mark it `NOT VERIFIED`, `NOT TESTED`, or `NOT STARTED` as appropriate.

When continuing work, append a new dated entry. Never rewrite or silently remove existing entries.

---

## 9. Security and privacy rules

- Never expose stack traces, database errors, exception details, or credentials to users
- Never log personal data (name, email), CSV contents, or secrets
- Never persist CSV file contents or raw CSV rows
- Document that name and email are stored; do not claim the app stores no personal data
- Use parameterised queries for all database operations
- Validate file type by parsing content, not only by extension
- Place the SQLite database file in a non-publicly-served directory

---

## 10. Approval gates

Do not proceed past these gates without explicit user approval:

1. **Before any implementation**: user has approved the plan
2. **Before major implementation**: PythonAnywhere ASGI test has passed (or fallback chosen)
3. **Before claiming deployment success**: live URL has been accessed and verified
4. **Before adding any feature**: it is in the approved MVP scope
5. **Before introducing any paid service**: explicit approval obtained

---

## 11. End-of-task report

After completing any meaningful task, report:

1. What was changed
2. Which files were created or updated and why
3. Which decisions were made or changed
4. Which tests or checks were actually performed and their results
5. What remains unverified
6. Any blockers or risks
7. The next logical step

---

*Last updated: 2026-10-12 (UI redesign, custom error pages, illustrated inline error, contact section, suggestions recorded)*

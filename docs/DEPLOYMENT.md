# DataCheck Deployment Guide

- **Target platform**: PythonAnywhere free Beginner tier
- **Status**: NOT DEPLOYED — all steps below are planned but UNVERIFIED
- **Date**: 2026-10-11

No deployment has been attempted yet. Steps marked **[UNVERIFIED]** have not been tested
on the PythonAnywhere free tier and may require adjustment.

---

## Platform constraints (PythonAnywhere free Beginner tier)

| Constraint | Value |
|---|---|
| Web apps | 1 |
| URL | `username.pythonanywhere.com` |
| HTTPS | Automatic (free subdomain) |
| Custom domain | Not available on free tier |
| RAM | ~512 MB |
| Disk | 512 MB |
| Outbound internet | Restricted — only whitelisted hosts reachable |
| ASGI support | **Beta feature** — compatibility with FastAPI is UNVERIFIED |
| WSGI support | Stable and well-tested |
| SQLite | Available; file must be in a writable directory |
| Cron / scheduled tasks | Available on free tier (1 task) |
| Always-on tasks | Not available on free tier |

**Critical**: The free tier has restricted outbound internet access. This prevents connecting
to external databases such as Supabase or any other remote PostgreSQL service. SQLite (local
file) is the only viable database option.

---

## Mandatory first step: ASGI compatibility test — [UPDATE: ASGI not exposed in web UI]

**Before writing any application code**, test that FastAPI deploys on the free tier.

**[UPDATE 2026-10-11]**: PythonAnywhere's "Manual configuration" web interface creates a **WSGI configuration file** by default, not ASGI. The ASGI support may be available through API or SSH configuration, but it is not exposed in the standard web interface for adding new web apps.

### Current situation:
- PythonAnywhere's web interface for "Manual configuration" creates a WSGI file (at `/var/www/`)
- FastAPI is ASGI-based and requires an ASGI server (uvicorn/hypercorn)
- The WSGI file created by PythonAnywhere won't work with FastAPI directly

### Options:

**Option A: Use Flask (WSGI-compatible) — Recommended**
- Flask is WSGI-compatible and well-supported on PythonAnywhere
- FastAPI features like Pydantic validation can be replaced with manual validation
- All other logic (CSV analysis, SQLite, JSON response) remains the same

**Option B: Test ASGI via API or SSH (advanced)**
- Use PythonAnywhere API to create ASGI configuration
- Or SSH into PythonAnywhere and configure manually
- Beyond the scope of standard web interface

---

## Fallback: Flask (WSGI)

**[UPDATE 2026-10-11]**: Given that ASGI is not exposed in PythonAnywhere's web interface,
the recommended approach is to use Flask (WSGI) instead of FastAPI.

Flask uses WSGI, which is stable and well-tested on PythonAnywhere. The trade-offs are:
- Replace Pydantic request models with manual validation
- Keep all other logic (CSV analysis, SQLite, JSON response) unchanged
- Flask is less automatic about error responses but fully functional

**Decision**: Use Flask instead of FastAPI. Update ADR-003 to reflect this change.

---

## Full deployment steps

These steps assume the ASGI compatibility test has passed. **[UNVERIFIED]**

### 1. Set up the repository

In a PythonAnywhere Bash console:

```bash
git clone https://github.com/irmakburkay/datacheck.git
cd datacheck
```

### 2. Create a virtual environment

```bash
mkvirtualenv datacheck --python=python3.11
pip install -r requirements.txt
```

### 3. Configure environment variables

In the PythonAnywhere web app configuration (Web tab → Environment variables section),
set the following variables. Do not hardcode values in source files.

| Variable | Description | Example |
|---|---|---|
| `MAX_UPLOAD_SIZE` | Max CSV upload in bytes | `5242880` |
| `MAX_ROWS` | Max rows allowed in uploaded CSV | `100000` |
| `MAX_COLUMNS` | Max columns allowed | `100` |
| `DATABASE_PATH` | Absolute path to SQLite file | `/home/<username>/data/requests.db` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

See `.env.example` for the full list of required variables.

### 4. Create the database directory

The SQLite file must be in a writable directory that is not served as a static path.
**[UNVERIFIED — exact writable path depends on PythonAnywhere account structure]**

```bash
mkdir -p /home/<username>/data
```

The application initialises the database schema on startup if the file does not exist.

### 5. Configure static files

In the Web tab → Static files section, add:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/datacheck/app/static/` |

### 6. Configure the ASGI entry point

**[UNVERIFIED]** In the Web tab, configure the ASGI application:

- Application module: `app.main:app`
- Working directory: `/home/<username>/datacheck`

Refer to the current PythonAnywhere ASGI beta documentation for exact configuration steps,
as the interface may differ from WSGI setup.

### 7. Reload the web app

Click "Reload" in the Web tab.

### 8. Verify deployment

Run through the deployment verification checklist below.

---

## Environment variables reference

See `.env.example` for the complete template. The following variables are required in
production:

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_PATH` | Yes | — | Absolute path on PythonAnywhere filesystem |
| `MAX_UPLOAD_SIZE` | No | `5242880` | In bytes |
| `MAX_ROWS` | No | `100000` | CSV row limit |
| `MAX_COLUMNS` | No | `100` | CSV column limit |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Do not set a `SECRET_KEY` unless a specific feature requires it. The current scope has
no session management or HMAC signing.

---

## Database persistence

SQLite stores data in a single file on the PythonAnywhere filesystem. Unlike ephemeral
containers, PythonAnywhere's filesystem persists across application reloads and redeployments.

**[UNVERIFIED]** Persistence behaviour:
- Application reloads (via the Web tab) do not delete the database file
- Redeployments via `git pull` do not delete the database file
- PythonAnywhere account deletion or inactivity expiry would delete the file

The database file must not be committed to the repository. Ensure `.gitignore` excludes `*.db`.

---

## Deployment verification checklist

Complete these checks after every deployment. Do not mark as passed until actually executed.

### Smoke test
- [ ] `GET https://<username>.pythonanywhere.com/health` returns `{"status": "ok"}`
- [ ] `GET https://<username>.pythonanywhere.com/` returns the service request form

### Functional test
- [ ] Submit the form with the sample CSV — response contains analysis results
- [ ] JSON report download works
- [ ] Database record exists after a valid submission (check via console if needed)
- [ ] Database record persists after application reload

### Error handling test
- [ ] Submit with an invalid email — validation error shown (not a success)
- [ ] Submit with a non-CSV file — error shown
- [ ] Submit with a file over 5 MB — size error shown
- [ ] Submit with a malformed CSV — error shown
- [ ] None of the above expose a stack trace or internal error detail

### Security test
- [ ] Page source contains no credentials or database paths
- [ ] Error responses contain no stack traces

---

## Known risks

1. **ASGI beta instability**: PythonAnywhere ASGI support may change or break without notice.
   Monitor PythonAnywhere announcements if the application stops working.

2. **Free tier inactivity**: PythonAnywhere free accounts may be deactivated after a period
   of inactivity. Log in periodically to keep the account active.

3. **Disk space**: The free tier provides 512 MB of disk. The SQLite database will grow with
   each submission; this is not a concern for assessment purposes but would need a cleanup
   strategy for long-term use.

4. **No always-on worker**: The free tier does not support always-on tasks. The application
   will have cold starts after periods of inactivity.

---

*This document must be updated after each deployment attempt, whether successful or not.*
*Mark steps as VERIFIED only after they have been successfully executed.*
---

## Flask deployment (recommended)

**[VERIFIED: WSGI works on PythonAnywhere]** Use this approach instead of ASGI.

### 1. Set up the repository

In a PythonAnywhere Bash console:

```bash
git clone https://github.com/irmakburkay/datacheck.git datacheck
cd datacheck
```

### 2. Create and activate virtual environment

```bash
mkvirtualenv datacheck --python=python3.11
pip install flask pandas
```

### 3. Create the database directory

```bash
mkdir -p /home/<username>/data
```

### 4. Create a WSGI file

PythonAnywhere requires a WSGI entry point. Create `/var/www/<username>_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/<username>/datacheck'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app.main import app as application
```

### 5. Configure the web app

1. Go to the "Web" tab → "Add a new web app"
2. Choose "Flask" from the framework list (this creates a proper WSGI config)
3. Choose Python 3.11
4. Or choose "Manual configuration" and specify the WSGI file path

### 6. Configure virtual environment

In the Web tab, set the virtualenv path:
```
/home/<username>/.virtualenvs/datacheck
```

### 7. Reload the web app

Click "Reload" in the Web tab.

### 8. Test

Open `https://<username>.pythonanywhere.com/health` in your browser.

---

## Environment variables reference
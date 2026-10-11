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

## Mandatory first step: ASGI compatibility test

**Before writing any application code**, test that FastAPI deploys on the free tier.

This test must be done manually in the PythonAnywhere web interface. It cannot be automated
from a local machine.

**[UNVERIFIED]** Steps:

1. Create a PythonAnywhere account (free Beginner tier)
2. Open a Bash console
3. Install fastapi and uvicorn in a virtual environment:
   ```bash
   mkvirtualenv datacheck --python=python3.11
   pip install fastapi uvicorn
   ```
4. Create a minimal test app:
   ```python
   # /home/<username>/test_app/main.py
   from fastapi import FastAPI
   app = FastAPI()

   @app.get("/health")
   def health():
       return {"status": "ok"}
   ```
5. Go to the Web tab → Add a new web app → Manual configuration → Python 3.11
6. Configure the ASGI entry point (see PythonAnywhere ASGI beta documentation)
7. Reload and test: `https://<username>.pythonanywhere.com/health`

**If this succeeds**: proceed with full implementation using FastAPI.  
**If this fails**: stop. Do not proceed with FastAPI. Evaluate the fallback below.

---

## Fallback: Flask (WSGI)

If FastAPI ASGI deployment fails on PythonAnywhere free tier, the fallback is Flask.

Flask uses WSGI, which is stable and well-tested on PythonAnywhere. The trade-offs are:
- Replace Pydantic request models with manual validation
- Keep all other logic (CSV analysis, SQLite, JSON response) unchanged
- Flask is less automatic about error responses but fully functional

**This fallback requires explicit user approval before implementation switches to Flask.**
Update ADR-003 in `DECISIONS.md` if the fallback is chosen.

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

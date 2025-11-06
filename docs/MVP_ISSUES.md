# MVP Issues for XSS Assistant

These 6 issues represent the minimum viable product (MVP) for the first release.

---

## Issue #1: FastAPI Skeleton + Health Endpoint

**Title:** Set up FastAPI backend skeleton with health check endpoint

**Description:**
Create the foundational FastAPI application structure with a basic health check endpoint. This establishes the backend framework and ensures the API can be started and tested.

**Acceptance Criteria:**
- [ ] FastAPI app initializes successfully
- [ ] `/health` endpoint returns 200 OK with system status
- [ ] `/` root endpoint returns API information
- [ ] Environment configuration loaded from `.env` file
- [ ] Database connection test in health endpoint
- [ ] API documentation available at `/docs`
- [ ] Uvicorn server starts without errors

**Technical Details:**
- Use Pydantic Settings for configuration
- Include CORS middleware
- Add structured logging
- Follow FastAPI best practices

**Difficulty:** S (Small - 1-2 hours)

**Files to Create/Modify:**
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/routers/health.py`

---

## Issue #2: Target CRUD API + Consent Upload

**Title:** Implement target management with consent-as-code validation

**Description:**
Build the API endpoints for creating, reading, updating, and deleting authorized testing targets. Each target must have an associated signed consent document that validates authorization.

**Acceptance Criteria:**
- [ ] `POST /api/v1/targets` creates target with consent
- [ ] `GET /api/v1/targets` lists all active targets
- [ ] `GET /api/v1/targets/{id}` retrieves target details
- [ ] `DELETE /api/v1/targets/{id}` soft-deletes target
- [ ] Consent document validated (expiry date, signature, scope)
- [ ] Invalid or expired consents rejected with 400/403
- [ ] All operations logged to audit trail
- [ ] Database models for Target and Consent created
- [ ] Pydantic schemas for request/response validation

**Technical Details:**
- SQLAlchemy models with relationships
- JSON storage for consent document
- Scope validation (allowed: xss_testing, dom_analysis, payload_testing, waf_analysis)
- Audit log entry for every target operation

**Difficulty:** M (Medium - 4-6 hours)

**Files to Create/Modify:**
- `backend/app/models/target.py`
- `backend/app/models/consent.py`
- `backend/app/routers/targets.py`
- `backend/app/schemas/target.py`

---

## Issue #3: Worker Scaffold + Job Enqueue

**Title:** Set up Celery worker with basic job queue integration

**Description:**
Create the worker process infrastructure using Celery and Redis. Implement job queueing so that when a session is created via the API, a background task is enqueued for the worker to process.

**Acceptance Criteria:**
- [ ] Celery app configured with Redis broker
- [ ] Worker process starts successfully (`python workers/worker.py`)
- [ ] `start_session_job` task defined and executable
- [ ] Task receives session ID and logs it
- [ ] Worker can connect to database to fetch session details
- [ ] Basic error handling and task retries configured
- [ ] Worker logs visible and structured
- [ ] Task status trackable via Celery result backend

**Technical Details:**
- Use Redis for both broker and result backend
- Configure task serialization (JSON)
- Set concurrency limit (2 workers for browser sessions)
- Add task timeout configuration

**Difficulty:** M (Medium - 4-6 hours)

**Files to Create/Modify:**
- `workers/worker.py`
- `workers/tasks.py`
- `workers/config.py`
- `backend/app/routers/sessions.py` (enqueue task on session create)

---

## Issue #4: Session Recorder API + Database Model

**Title:** Implement session recording API and database schema

**Description:**
Create the Session model and API endpoints for managing testing sessions. Sessions track the lifecycle of browser automation jobs, including status, timestamps, approval state, and recording metadata.

**Acceptance Criteria:**
- [ ] Session database model created with status enum
- [ ] `POST /api/v1/sessions` creates session and enqueues worker task
- [ ] `GET /api/v1/sessions` lists sessions with status filter
- [ ] `GET /api/v1/sessions/{id}` retrieves session details
- [ ] `DELETE /api/v1/sessions/{id}` cancels running session
- [ ] Session statuses: pending, running, pending_approval, approved, completed, failed, cancelled
- [ ] Foreign key relationship to Target
- [ ] Recording metadata fields (recording_path, screenshot_count, etc.)
- [ ] Timestamps tracked (started_at, completed_at, approval_requested_at)

**Technical Details:**
- SQLAlchemy model with enum for status
- Validation: session requires authorized target
- Validation: consent must not be expired
- Audit log for session lifecycle events

**Difficulty:** M (Medium - 5-7 hours)

**Files to Create/Modify:**
- `backend/app/models/session.py`
- `backend/app/routers/sessions.py`
- `backend/app/schemas/session.py`

---

## Issue #5: Human-Approval Endpoint + Basic UI Mock

**Title:** Build human-in-the-loop approval workflow

**Description:**
Implement the approval mechanism where workers can request human approval when suspicious patterns are detected. Create API endpoint for approval and a basic workflow to update session status.

**Acceptance Criteria:**
- [ ] `POST /api/v1/sessions/{id}/approve` endpoint created
- [ ] Accepts approval decision (approved: true/false) and notes
- [ ] Updates session status from PENDING_APPROVAL to APPROVED or CANCELLED
- [ ] Records approval timestamp and user ID
- [ ] Worker task can check approval status (polling or event-based)
- [ ] Audit log records approval decision
- [ ] Returns 400 if session not in PENDING_APPROVAL status
- [ ] Documentation for approval workflow in README

**Technical Details:**
- Pydantic schema for approval request
- Database update with transaction safety
- Future enhancement: WebSocket or Redis pub/sub for real-time notifications
- For MVP: worker can poll database for status change

**Difficulty:** M (Medium - 4-5 hours)

**Files to Create/Modify:**
- `backend/app/routers/sessions.py` (add approval endpoint)
- `workers/browser.py` (add wait_for_approval method)
- `docs/APPROVAL_WORKFLOW.md`

---

## Issue #6: CI Pipeline Setup

**Title:** Configure GitHub Actions CI with linting and unit tests

**Description:**
Set up continuous integration pipeline to automatically run linting, unit tests, and optional integration tests on every push and pull request.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow defined (`.github/workflows/ci.yml`)
- [ ] Lint job: runs ruff/flake8 on backend and workers
- [ ] Test job: runs pytest with PostgreSQL and Redis services
- [ ] Playwright browsers installed in CI
- [ ] Unit tests pass (minimum 3 tests for routes)
- [ ] Coverage report generated (min 60% for MVP)
- [ ] Optional: Juice Shop integration test job (runs on PRs only)
- [ ] Optional: Security scan with bandit and safety
- [ ] Build check verifies imports work

**Technical Details:**
- Use GitHub Actions service containers for PostgreSQL and Redis
- Cache pip dependencies for faster builds
- Separate jobs for lint, test, and integration
- Upload coverage to Codecov (optional)

**Difficulty:** S (Small - 2-3 hours)

**Files to Create/Modify:**
- `.github/workflows/ci.yml`
- `tests/conftest.py` (pytest fixtures)
- `tests/test_api/test_health.py`
- `tests/test_api/test_targets.py`
- `tests/test_api/test_sessions.py`

---

## Priority Order

Suggested implementation order:
1. Issue #1 (FastAPI skeleton) - Foundation
2. Issue #2 (Target CRUD) - Core functionality
3. Issue #4 (Session model) - Core functionality
4. Issue #3 (Worker scaffold) - Background processing
5. Issue #5 (Human approval) - Key feature
6. Issue #6 (CI pipeline) - Quality assurance

---

## Estimation

- **Total MVP time:** ~20-30 hours (1 week for solo developer, 3-4 days for team)
- **S issues:** 3-5 hours total
- **M issues:** 17-25 hours total

---

## Notes

- All issues require compliance with security constraints (consent-as-code, audit logging)
- No payload generation or exploitation code in MVP
- Focus on infrastructure and human-in-the-loop workflow
- Testing framework can be expanded post-MVP

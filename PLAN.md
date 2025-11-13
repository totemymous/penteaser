# XSS Assistant - Technical Plan

> High-level architecture, deployment strategy, and implementation roadmap

---

## 🎯 Project Vision

Build a **human-supervised XSS testing assistant** for authorized penetration testing and security education. The tool combines automated reconnaissance with human decision-making to ensure ethical and controlled security testing.

**Core Principles:**
- **Consent-first**: No testing without explicit authorization
- **Human-in-the-loop**: Critical decisions require operator approval
- **Audit everything**: Immutable logs for accountability
- **Transparent operation**: Headful browser mode for visibility

---

## 🏗️ System Architecture

### High-Level Components

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend/CLI (Future)                    │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                 │
│  ┌─────────────┬──────────────┬────────────┬──────────────┐  │
│  │   Auth      │   Targets    │  Sessions  │   Reports    │  │
│  │ (OAuth2/    │   (CRUD +    │  (Job Mgmt │  (Markdown/  │  │
│  │  API Key)   │   Consent)   │   + State) │    PDF)      │  │
│  └─────────────┴──────────────┴────────────┴──────────────┘  │
└───────────────────────────┬──────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────┐   ┌──────────────────────┐
│   PostgreSQL DB       │   │   Redis Queue        │
│                       │   │                      │
│  - users              │   │  - Job queue         │
│  - targets            │   │  - Task state        │
│  - consents           │   │  - Session cache     │
│  - sessions           │   └──────────┬───────────┘
│  - findings           │              │
│  - audit_logs         │              ▼
└───────────────────────┘   ┌──────────────────────┐
                            │  Worker Process      │
                            │  (Celery/RQ)         │
                            │                      │
                            │  - Job polling       │
                            │  - Browser control   │
                            │  - Session recording │
                            └──────────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │  Playwright/Selenium │
                            │  (Chrome Headful)    │
                            │                      │
                            │  - DOM analysis      │
                            │  - Interaction       │
                            │  - Screenshot/video  │
                            └──────────────────────┘
```

### Data Flow

1. **User creates target** → Backend validates consent file → Stores in DB
2. **User starts session** → Backend creates job → Redis queue
3. **Worker picks job** → Launches browser (headful) → Begins analysis
4. **Suspicious pattern found** → Worker pauses → Sets status `pending_approval`
5. **User notified** → Reviews in browser → Approves or rejects
6. **If approved** → Worker continues with guided testing → Records findings
7. **Session complete** → Worker generates report → Stores encrypted recording
8. **User retrieves report** → Backend serves Markdown/PDF

---

## 🔧 Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0+ with asyncio support
- **Validation**: Pydantic v2
- **Auth**: OAuth2 (password flow) + API Key with JWT
- **Migrations**: Alembic

### Worker & Queue
- **Queue**: Redis 6+
- **Task Queue**: Celery 5+ (or RQ as lightweight alternative)
- **Browser Automation**: Playwright (preferred) or Selenium
- **Browser**: Chromium/Chrome (headful mode)

### Database & Storage
- **RDBMS**: PostgreSQL 14+
- **Session Storage**: Local filesystem or S3-compatible (encrypted with Fernet)
- **Encryption**: `cryptography` library (Fernet symmetric encryption)

### Testing & CI
- **Unit Tests**: pytest + pytest-asyncio
- **Coverage**: pytest-cov
- **Linting**: ruff (or flake8 + black)
- **Type Checking**: mypy (optional)
- **CI Platform**: GitHub Actions
- **Sandbox Target**: OWASP Juice Shop (npm-based)

### Deployment (No Docker)
- **Service Manager**: systemd (Linux) or Supervisor
- **Reverse Proxy**: Nginx (optional, for production)
- **Process Manager**: systemd units for backend + worker
- **Configuration Management**: Ansible playbook (optional)

---

## 📦 Project Structure

```
penteaser/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (Pydantic BaseSettings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── auth.py              # OAuth2/JWT utilities
│   │   ├── dependencies.py      # FastAPI dependencies (auth, db)
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── target.py
│   │   │   ├── consent.py
│   │   │   ├── session.py
│   │   │   ├── finding.py
│   │   │   └── audit_log.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── auth.py
│   │   │   ├── targets.py
│   │   │   ├── sessions.py
│   │   │   └── reports.py
│   │   ├── schemas/             # Pydantic schemas (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── target.py
│   │   │   ├── session.py
│   │   │   └── finding.py
│   │   └── services/            # Business logic
│   │       ├── __init__.py
│   │       ├── consent.py       # Consent validation
│   │       ├── recorder.py      # Session recording
│   │       ├── analyzer.py      # Pattern detection
│   │       └── report.py        # Report generation
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── workers/
│   ├── __init__.py
│   ├── worker.py                # Celery/RQ worker entry point
│   ├── tasks.py                 # Task definitions
│   ├── browser.py               # Playwright/Selenium wrapper
│   └── config.py                # Worker configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api/
│   │   ├── test_health.py
│   │   ├── test_targets.py
│   │   └── test_sessions.py
│   ├── test_services/
│   │   ├── test_consent.py
│   │   └── test_recorder.py
│   └── test_integration/
│       └── test_juice_shop.py   # E2E with Juice Shop
├── docs/
│   ├── SECURITY_CHECKLIST.md
│   ├── consent-example.json
│   └── API.md                   # API documentation
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── scripts/
│   └── setup_db.sh              # Database initialization script
├── .gitignore
├── README.md
├── PLAN.md                      # This file
├── CONTRIBUTING.md
└── LICENSE
```

---

## 🚀 Deployment Strategy (No Docker)

### Development Environment

```bash
# 1. Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements-dev.txt

# 3. Setup PostgreSQL locally
sudo apt install postgresql
sudo -u postgres createdb xss_assistant

# 4. Setup Redis
sudo apt install redis-server
sudo systemctl start redis

# 5. Run migrations
cd backend && alembic upgrade head

# 6. Start backend (dev mode)
uvicorn backend.app.main:app --reload --port 8000

# 7. Start worker (separate terminal)
celery -A workers.worker worker --loglevel=info
```

### Production Deployment

#### Using systemd

**Backend Service** (`/etc/systemd/system/xss-assistant-api.service`):
```ini
[Unit]
Description=XSS Assistant API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=xss-assistant
Group=xss-assistant
WorkingDirectory=/opt/xss-assistant
Environment="PATH=/opt/xss-assistant/.venv/bin"
ExecStart=/opt/xss-assistant/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Worker Service** (`/etc/systemd/system/xss-assistant-worker.service`):
```ini
[Unit]
Description=XSS Assistant Worker
After=network.target redis.service

[Service]
Type=forking
User=xss-assistant
Group=xss-assistant
WorkingDirectory=/opt/xss-assistant
Environment="PATH=/opt/xss-assistant/.venv/bin"
ExecStart=/opt/xss-assistant/.venv/bin/celery -A workers.worker worker --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name xss-assistant.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 🧪 Testing Strategy

### Test Pyramid

1. **Unit Tests** (70%)
   - FastAPI route handlers
   - Service layer logic (consent validation, pattern detection)
   - Utility functions
   - Database models (SQLAlchemy)

2. **Integration Tests** (20%)
   - API endpoint workflows (create target → start session → get report)
   - Database transactions
   - Worker job lifecycle
   - Session recording pipeline

3. **E2E Tests** (10%)
   - Full workflow with Juice Shop sandbox
   - Human-approval simulation
   - Report generation end-to-end

### Test Execution

```bash
# Unit tests
pytest tests/test_api tests/test_services -v

# Integration tests
pytest tests/test_integration -v

# With coverage
pytest --cov=backend --cov=workers --cov-report=html

# Linting
ruff check backend/ workers/
```

### CI Pipeline (GitHub Actions)

See `.github/workflows/ci.yml`:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Run linter (ruff/flake8)
5. Run unit tests
6. (Optional) Start Juice Shop in background
7. Run integration tests
8. Upload coverage report

---

## 🔐 Security & Compliance

### Consent-as-Code

Every target requires a signed JSON consent file:

```json
{
  "target_id": "uuid-here",
  "target_url": "https://example.com",
  "authorized_by": "John Doe",
  "authorization_email": "john@example.com",
  "authorization_date": "2025-01-15",
  "expiry_date": "2025-02-15",
  "scope": ["xss_testing", "dom_analysis"],
  "signature": "base64-signed-hash"
}
```

### Audit Trail

All operations logged to `audit_logs` table:
- User ID
- Timestamp
- Action (target_created, session_started, payload_tested, etc.)
- Target ID
- Consent reference
- IP address
- User agent

### Access Control

- **Authentication**: OAuth2 password flow or API key
- **Authorization**: RBAC (roles: admin, tester, viewer)
- **Rate Limiting**: Per-user and per-target limits
- **Session Expiry**: JWT tokens expire after configurable time

---

## 📊 MVP Milestones

### Milestone 1: Core Infrastructure (Week 1-2)
- [ ] FastAPI skeleton + health endpoint
- [ ] Database models (users, targets, consents, sessions)
- [ ] Target CRUD API with consent validation
- [ ] Basic authentication (API key)
- [ ] CI pipeline (lint + unit tests)

### Milestone 2: Worker & Browser (Week 3-4)
- [ ] Celery/RQ worker setup
- [ ] Playwright browser wrapper (headful mode)
- [ ] Session job lifecycle (create → execute → complete)
- [ ] Basic DOM fingerprinting (no payloads)
- [ ] Human-approval endpoint

### Milestone 3: Testing & Reporting (Week 5-6)
- [ ] Integration tests with Juice Shop
- [ ] Session metadata recording
- [ ] Markdown report generation
- [ ] Audit log implementation
- [ ] Documentation completion

### Milestone 4: Advanced Features (Week 7-8)
- [ ] Payload generation module (with consent check)
- [ ] WAF detection logic
- [ ] PDF report export
- [ ] OAuth2 authentication
- [ ] Production deployment guide

---

## 🛠️ Development Workflow

### Local Development

1. Create feature branch: `git checkout -b feature/xyz`
2. Make changes
3. Run tests: `pytest`
4. Run linter: `ruff check .`
5. Commit: `git commit -m "feat: add xyz"`
6. Push and create PR

### PR Requirements

- All tests pass
- Linter passes (no errors)
- Code coverage > 80%
- Documentation updated
- Security checklist reviewed (for sensitive features)

### Code Review Checklist

- [ ] No hardcoded credentials
- [ ] Consent validation present for testing features
- [ ] Audit logging for sensitive operations
- [ ] Error handling with proper HTTP status codes
- [ ] Input validation (Pydantic schemas)
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS prevention in API responses
- [ ] Rate limiting for public endpoints

---

## 📈 Future Enhancements

- **Web Dashboard**: React/Vue frontend for session management
- **Multi-target Campaigns**: Batch testing with reporting
- **Plugin System**: Custom analyzers and payload generators
- **Machine Learning**: Pattern detection improvement
- **Responsible Disclosure**: Built-in report templates for vendors
- **Collaboration**: Team workspaces and shared sessions
- **Cloud Deployment**: Terraform/Ansible automation

---

## 📚 References

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Playwright Documentation](https://playwright.dev/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)

---

**Last Updated**: 2025-01-15
**Document Owner**: Architecture Team
**Review Cycle**: Bi-weekly

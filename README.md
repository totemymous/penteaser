# XSS Assistant

> **Authorized Security Testing & Education Tool**

A human-in-the-loop XSS detection assistant designed exclusively for **authorized penetration testing** and **educational purposes** in controlled, sandboxed environments.

---

## ⚠️ LEGAL & ETHICAL WARNINGS

**READ THIS BEFORE USE:**

- ✅ **ONLY USE ON AUTHORIZED TARGETS** - You must have explicit written permission
- ✅ **EDUCATIONAL/TESTING ONLY** - Designed for security research and training
- ⚠️ **POWERFUL CAPABILITIES** - Includes advanced testing features (WAF analysis, payload testing, exploitation techniques)
- 🔒 **CONSENT-AS-CODE MANDATORY** - A signed JSON consent file is required before any operation
- 👤 **HUMAN-IN-THE-LOOP REQUIRED** - All deep testing requires explicit operator approval

**This tool is designed for authorized penetration testers, security researchers, and students in controlled environments.**

**By using this software, you agree to:**
1. Only test systems you own or have written authorization to test
2. Comply with all applicable laws and regulations
3. Accept full responsibility for your actions

**Recommended Use Cases:**
- Authorized penetration testing engagements
- Bug bounty programs with explicit scope
- Security research in controlled lab environments
- Educational purposes with sandboxed applications (e.g., OWASP Juice Shop)
- Internal security assessments with management approval

---

## 🎯 Features

- **Human-in-the-Loop**: All deep testing requires explicit operator approval
- **Consent Management**: Mandatory signed consent files (consent-as-code)
- **Advanced Testing**: WAF analysis, payload generation, and exploitation techniques for authorized testing
- **Session Recording**: Immutable audit trail with metadata (encrypted storage)
- **Headful Browser Mode**: Transparent operation with visual feedback
- **Report Generation**: Markdown & PDF exports with remediation guidance
- **Sandbox Testing**: Built-in OWASP Juice Shop integration for safe practice

---

## 🏗️ Architecture (No Docker)

All services run on bare metal, VMs, or developer machines using systemd/supervisor:

```
┌─────────────────┐
│   FastAPI       │  ← REST API (uvicorn)
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────────────────┬──────────────┐
    ▼                     ▼              ▼
┌─────────┐         ┌──────────┐    ┌────────┐
│PostgreSQL│        │  Redis   │    │ Worker │
│   DB     │        │  Queue   │    │Process │
└──────────┘        └──────────┘    └───┬────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Playwright/  │
                                │  Selenium     │
                                │  (headful)    │
                                └───────────────┘
```

**Components:**
- **Backend**: FastAPI application (Python 3.11+)
- **Worker**: Celery/RQ task queue for browser automation
- **Database**: PostgreSQL for findings, users, consents
- **Cache/Queue**: Redis for job management
- **Browser**: Playwright or Selenium in headful mode

---

## 🚀 Quickstart

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Chrome/Chromium + matching ChromeDriver
- (Optional) OWASP Juice Shop for sandbox testing

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/penteaser.git
   cd penteaser
   ```

2. **Create Python virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Setup PostgreSQL**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt install postgresql postgresql-contrib

   # Create database
   sudo -u postgres createdb xss_assistant
   sudo -u postgres psql -c "CREATE USER xss_user WITH PASSWORD 'your_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE xss_assistant TO xss_user;"
   ```

5. **Setup Redis**
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt install redis-server

   # Start Redis
   sudo systemctl start redis
   sudo systemctl enable redis
   ```

6. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your database and Redis connection strings
   ```

7. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

8. **Start the backend**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. **Start the worker (separate terminal)**
   ```bash
   source .venv/bin/activate
   python workers/worker.py
   # Or with Celery: celery -A backend.app.celery worker --loglevel=info
   ```

10. **Access the API**
    - API: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - Health check: http://localhost:8000/health

---

## 🧪 Sandbox Testing with OWASP Juice Shop

For safe, legal testing, use OWASP Juice Shop:

### Option 1: Separate VM (Recommended)
```bash
# On a separate VM or container
git clone https://github.com/juice-shop/juice-shop.git
cd juice-shop
npm install
npm start
# Juice Shop runs on http://localhost:3000
```

### Option 2: Local Instance
```bash
npm install -g juice-shop
juice-shop
```

**Configure XSS Assistant to target Juice Shop:**
1. Create a consent file (see `docs/consent-example.json`)
2. Add target via API: `POST /api/v1/targets` with Juice Shop URL
3. Start a session with human approval

---

## 📝 Configuration

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://xss_user:your_password@localhost/xss_assistant

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this
API_KEY_SALT=your-api-key-salt

# Worker
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Browser
BROWSER_TYPE=playwright  # or selenium
HEADFUL_MODE=true

# Storage
SESSION_RECORDINGS_PATH=/var/lib/xss-assistant/recordings
ENCRYPTION_KEY=your-encryption-key

# Security & Compliance (Optional - for development/lab environments)
# Set REQUIRE_CONSENT=false to disable consent validation (lab use only)
# Set AUTO_APPROVE_SESSIONS=true to bypass human approval workflow
# Set MINIMAL_LOGGING=true for reduced audit logging
REQUIRE_CONSENT=true
AUTO_APPROVE_SESSIONS=false
MINIMAL_LOGGING=false
```

### Configuration Modes

**Production Mode** (Default - Maximum Security):
```env
REQUIRE_CONSENT=true
AUTO_APPROVE_SESSIONS=false
MINIMAL_LOGGING=false
```

**Lab/Development Mode** (Flexible for testing):
```env
REQUIRE_CONSENT=false
AUTO_APPROVE_SESSIONS=true
MINIMAL_LOGGING=true
```

**⚠️ Warning:** Lab mode should only be used in controlled, authorized environments (personal labs, sandboxed VMs, or authorized testing ranges).

---

## 🧪 Running Tests

```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=backend --cov-report=html tests/

# Linting
flake8 backend/ workers/
# or
ruff check backend/ workers/
```

---

## 🔒 Security & Compliance

**Flexible Security Configuration:**

XSS Assistant supports multiple security modes for different use cases:

### Production Mode (Default)
- **Consent-as-Code**: All targets require signed JSON consent file
- **Human-in-the-Loop**: Deep testing requires explicit operator approval
- **Audit Trail**: Full immutable logs for all operations
- **Access Control**: OAuth2 + API Key authentication with RBAC
- **Encrypted Storage**: Session recordings encrypted at rest

### Lab/Development Mode (Optional)
- **Optional Consent**: Consent validation can be disabled (`REQUIRE_CONSENT=false`)
- **Auto-Approval**: Sessions can run without human approval (`AUTO_APPROVE_SESSIONS=true`)
- **Minimal Logging**: Reduced audit logging for performance (`MINIMAL_LOGGING=true`)

**Configuration:**
```env
# Production (default)
REQUIRE_CONSENT=true
AUTO_APPROVE_SESSIONS=false
MINIMAL_LOGGING=false

# Lab/Dev mode
REQUIRE_CONSENT=false
AUTO_APPROVE_SESSIONS=true
MINIMAL_LOGGING=true
```

See `docs/SECURITY_CHECKLIST.md` for full compliance checklist.

---

## 📊 Human-in-the-Loop Workflow

1. **Discovery**: Worker performs passive DOM analysis (no payloads)
2. **Detection**: Suspicious patterns flagged as `pending_approval`
3. **Notification**: User receives alert via dashboard/API
4. **Review**: User opens headful browser session to inspect
5. **Decision**: User manually verifies or approves deeper guided testing
6. **Recording**: All actions logged to audit trail
7. **Report**: Findings exported to Markdown/PDF

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Important**: All contributions must adhere to security and ethical constraints. PRs introducing exploit code, WAF bypass, or unauthorized scanning capabilities will be rejected.

---

## 📄 License

[MIT License](LICENSE) - See LICENSE file for details.

**Disclaimer**: This software is provided "as is" for educational and authorized testing purposes only. The authors and contributors are not responsible for misuse or damage caused by this software.

---

## 🆘 Support

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues (use provided templates)
- **Security Concerns**: See [SECURITY.md](docs/SECURITY_CHECKLIST.md)

---

## 🗺️ Roadmap

- [x] MVP: FastAPI backend + basic endpoints
- [x] Worker scaffold with Playwright
- [x] CI/CD pipeline
- [ ] OAuth2 authentication
- [ ] PDF report generation
- [ ] Advanced session replay viewer
- [ ] Multi-target campaign management
- [ ] Responsible disclosure templates

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**

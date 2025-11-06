# Contributing to XSS Assistant

Thank you for your interest in contributing to XSS Assistant! This document provides guidelines for contributing to this authorized security testing tool.

---

## 🚨 Important: Security and Ethics

**Before contributing, understand these requirements:**

1. **All contributions must support ONLY authorized testing**
   - No features for unauthorized scanning or evasion
   - All testing features must include consent validation
   - Human-in-the-loop approval required for sensitive operations

2. **Prohibited contributions:**
   - Features that enable unauthorized testing
   - Techniques specifically designed for evasion or stealth
   - Automated exploitation without human approval
   - Mass scanning capabilities
   - Features that bypass consent-as-code requirements

3. **Required for all contributions:**
   - Audit logging for sensitive operations
   - Consent validation where applicable
   - Clear documentation of ethical use
   - Security review for testing features

**If you're unsure whether your contribution aligns with these principles, open an issue to discuss before coding.**

---

## 🤝 Ways to Contribute

- **Bug reports** - Report issues or unexpected behavior
- **Feature requests** - Suggest new capabilities (within ethical boundaries)
- **Documentation** - Improve README, guides, or code comments
- **Code** - Fix bugs or implement approved features
- **Testing** - Write tests or test with authorized sandbox environments
- **Security review** - Review code for vulnerabilities

---

## 📋 Getting Started

### 1. Set Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/penteaser.git
cd penteaser

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements-dev.txt

# Set up PostgreSQL and Redis (see README.md)

# Run tests
pytest tests/
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring

### 3. Make Your Changes

- Follow existing code style (PEP 8 for Python)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "feat: add consent validation to session endpoint"
git commit -m "fix: correct database migration for targets table"
git commit -m "docs: update quickstart guide with Redis setup"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Run Tests and Linting

```bash
# Linting
ruff check backend/ workers/

# Unit tests
pytest tests/ -v

# With coverage
pytest --cov=backend --cov=workers --cov-report=term
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub using the PR template.

---

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Mirror the source code structure
- Use pytest fixtures for common setup
- Aim for >80% code coverage

Example test structure:
```python
def test_create_target_with_valid_consent(client, db_session):
    """Test target creation with valid consent document"""
    consent = {
        "authorized_by": "John Doe",
        "authorization_email": "john@example.com",
        # ... full consent
    }
    response = client.post("/api/v1/targets", json={
        "name": "Test Target",
        "url": "https://juice-shop.example.com",
        "consent": consent
    })
    assert response.status_code == 201
    assert response.json()["is_authorized"] == True
```

### Integration Testing

Use OWASP Juice Shop for integration tests:
```bash
# Start Juice Shop in separate terminal
cd /path/to/juice-shop && npm start

# Run integration tests
pytest tests/test_integration/ -v
```

---

## 📝 Code Style Guidelines

### Python

- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and small
- Document complex logic with comments
- Use docstrings for all public functions/classes

Example:
```python
def validate_consent(consent: ConsentCreate) -> bool:
    """
    Validate consent document for authorization.

    Args:
        consent: Consent document to validate

    Returns:
        True if consent is valid and not expired

    Raises:
        ValueError: If consent is invalid or expired
    """
    if consent.expiry_date <= datetime.utcnow():
        raise ValueError("Consent has expired")
    return True
```

### FastAPI

- Use Pydantic models for request/response
- Include OpenAPI documentation strings
- Use dependency injection for database sessions
- Handle errors with appropriate HTTP status codes

### SQLAlchemy

- Use declarative models
- Define relationships explicitly
- Add indexes for frequently queried fields
- Use migrations (Alembic) for schema changes

---

## 🔍 Code Review Process

All pull requests require:

1. **CI passing** - All tests and linting must pass
2. **Code review** - At least one maintainer approval
3. **Security review** - For features involving testing/automation
4. **Documentation** - README/docs updated if needed

### Review Checklist

Reviewers will check:

- [ ] Code follows style guidelines
- [ ] Tests cover new functionality
- [ ] No hardcoded secrets or credentials
- [ ] Consent validation present (if applicable)
- [ ] Audit logging for sensitive operations
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] Commit messages are clear

---

## 🛡️ Security Review Requirements

Features involving these areas require security review:

- Browser automation and interaction
- Payload generation or testing
- Consent validation logic
- Authentication/authorization
- Database migrations
- External API integrations

For security review:
1. Tag your PR with `security-review` label
2. Explain the security implications in PR description
3. Reference relevant consent/audit logging code
4. Wait for security team approval

---

## 📚 Documentation Standards

### Code Documentation

- All public APIs must have docstrings
- Complex algorithms need inline comments
- Configuration options documented in README

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Document new API endpoints in docs/API.md

### Architecture Documentation

- Update PLAN.md for architectural changes
- Document design decisions in ADRs (if applicable)

---

## 🐛 Reporting Bugs

Use the bug report template and include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

**Security vulnerabilities:** Report privately to maintainers, not in public issues.

---

## 💡 Suggesting Features

Use the feature request template and include:

- Use case and problem it solves
- Proposed solution
- Ethical considerations (consent, approval, logging)
- Implementation ideas (optional)

---

## 🎯 Priority Issues

Check these labels for good starting points:

- `good first issue` - Beginner-friendly
- `help wanted` - Maintainers need help
- `documentation` - Docs improvements
- `bug` - Bug fixes needed

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## 🙏 Thank You!

Your contributions help make security testing more accessible, ethical, and effective. We appreciate your time and effort!

**Questions?** Open an issue or reach out to maintainers.

---

**Remember: Always test ethically, always get authorization, always prioritize responsible disclosure.**

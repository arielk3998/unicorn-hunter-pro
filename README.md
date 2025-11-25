# Unicorn Hunter Pro

AI-powered job application tracker with intelligent resume optimization, ATS analysis, and automated job matching. Built to help you hunt down your dream role with data-driven insights and a beautiful desktop interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Desktop Application](#desktop-application)
  - [API Server](#api-server)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Security](#security)
- [Performance](#performance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support This Project](#support-this-project)
- [License](#license)

## Overview

I built Unicorn Hunter Pro after realizing that job hunting is a data problem. Traditional application tracking is manual, resumes get rejected by ATS systems for fixable reasons, and there's no good way to measure which roles actually match your skills. This toolkit solves all three.

The system combines a FastAPI backend with enterprise-grade security, a SQLite persistence layer, an AI-powered matching engine, and a Tkinter desktop GUI. It generates professional resumes, analyzes ATS compatibility, tracks applications, and scores job matches—all while keeping your data local and private.

## Features

### Core Capabilities

- **Profile Management**: Store skills, experience, education, and contact info in structured formats
- **Resume Generation**: Export professional resumes in multiple formats (Markdown, HTML, PDF coming soon)
- **ATS Analysis**: Get detailed reports on keyword gaps, formatting issues, and compatibility scores
- **Job Matching Engine**: Intelligent scoring based on skills, experience, location, and role fit
- **Application Tracking**: Monitor status, dates, notes, and outcomes for every application
- **Document Storage**: Save cover letters, resumes, and supporting docs per application

### Technical Features

- **Unified Authentication**: API key + JWT access/refresh tokens with bcrypt password hashing
- **Rate Limiting**: Redis-backed sliding window with in-memory fallback for multi-instance deployments
- **Structured Logging**: JSON output with correlation IDs for request tracing
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Performance Profiling**: Built-in benchmarking for matching and document generation
- **Desktop GUI**: Native Tkinter interface with tabs for auth, dashboard, profiles, jobs, and applications
- **Cross-Platform Scrolling**: Mouse wheel support for Windows, macOS, and Linux

### API Endpoints

- `POST /auth/register` - Create account (email + password only)
- `POST /auth/login` - Authenticate and receive token pair
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Revoke refresh token
- `POST /profiles/` - Create or update profile
- `GET /profiles/{id}` - Retrieve profile
- `POST /jobs/` - Add job listing
- `GET /jobs/` - List all jobs
- `POST /applications/` - Create application
- `GET /applications/` - List applications
- `POST /match` - Score job-profile match
- `POST /documents/generate` - Generate resume
- `POST /documents/ats-report` - Analyze ATS compatibility

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)
- Redis (optional, for distributed rate limiting)

### Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/arielk3998/unicorn-hunter-pro.git
cd unicorn-hunter-pro
```

Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables (optional):

```bash
# API security
export API_KEY="your-secret-api-key"
export JWT_SECRET="your-jwt-secret"
export REFRESH_SECRET="your-refresh-secret"

# Database
export DATABASE_PATH="data/resume_toolkit.db"

# Redis (if available)
export REDIS_URL="redis://localhost:6379"
```

Initialize the database:

```bash
python -c "from app.infrastructure.database.sqlite_schema import ensure_schema; ensure_schema('data/resume_toolkit.db')"
```

## Usage

### Desktop Application

Launch the GUI for the full visual experience:

```bash
python unicorn_hunter_gui.py
```

The application opens with tabs for login/register, dashboard stats, profile creation, job browsing, and application tracking. All data syncs with the API backend running on port 8002 by default.

**First Run**:
1. Start the API server (see below)
2. Launch the GUI
3. Register with your email and password
4. Create your profile in the Profile tab
5. Add jobs and track applications

### API Server

Run the FastAPI backend for programmatic access or to support the GUI:

```bash
uvicorn app.presentation.api.main:app --host 127.0.0.1 --port 8002 --reload
```

Access the interactive API documentation at `http://127.0.0.1:8002/docs`.

**Production Deployment**:
```bash
uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Use a reverse proxy (nginx, Traefik) and set `--proxy-headers` for proper client IP forwarding.

## Architecture

The project follows clean architecture principles with clear separation of concerns:

```
app/
├── domain/              # Business entities and models
│   └── models.py        # Profile, Job, Application, Document (Pydantic v2)
├── application/         # Use cases and services
│   └── services/
│       ├── profile_service.py
│       ├── job_service.py
│       ├── application_service.py
│       ├── document_service.py
│       ├── matching_service.py
│       └── user_service.py
├── infrastructure/      # External interfaces
│   ├── database/
│   │   ├── sqlite_schema.py
│   │   ├── sqlite_profile_repo.py
│   │   ├── sqlite_job_repo.py
│   │   ├── sqlite_application_repo.py
│   │   ├── sqlite_document_repo.py
│   │   └── sqlite_user_repo.py
│   ├── cache/
│   │   └── redis_rate_limiter.py
│   └── logging/
│       └── structured_logger.py
└── presentation/        # API and UI
    └── api/
        ├── main.py
        ├── security.py
        └── routers/
            └── auth_router.py
```

**Key Design Decisions**:

- **Pydantic v2**: All models use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility
- **Repository Pattern**: Abstracts database operations for easier testing and future migrations
- **Event Bus**: Pub/sub pattern for decoupled communication (currently in-memory, extensible to Redis)
- **Factory Pattern**: `create_app()` enables test isolation and configuration injection
- **Middleware Chain**: Correlation IDs → Rate limiting → Security headers → Routers

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | None | Optional API key for legacy auth |
| `JWT_SECRET` | (insecure default) | Secret for signing JWT access tokens |
| `REFRESH_SECRET` | (insecure default) | Secret for refresh token validation |
| `DATABASE_PATH` | `data/resume_toolkit.db` | SQLite database file path |
| `REDIS_URL` | None | Redis connection string (optional) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Rate Limiting

Default: 100 requests per 60 seconds per IP. Modify in `app/presentation/api/main.py`:

```python
rate_limiter = RedisRateLimiter(
    redis_url=redis_url,
    max_requests=200,  # Increase limit
    window_seconds=60
)
```

### Security Headers

CSP and HSTS are enabled by default. Adjust in `main.py` if serving over HTTP locally:

```python
# Disable HSTS for local development
response.headers.pop("Strict-Transport-Security", None)
```

## Development

### Running Tests

Execute the full test suite with coverage:

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

View the HTML coverage report:

```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Performance Profiling

Benchmark the matching engine and document generation:

```bash
python scripts/perf_profile.py
```

Sample output:
```
MatchingEngine.calculate_match: mean=0.00ms, p95=0.00ms
DocumentService.generate_resume: mean=125.32ms, p95=142.18ms
DocumentService.generate_ats_report: mean=133.47ms, p95=151.22ms
```

### Code Quality

Run linters and formatters:

```bash
# Type checking
mypy app/

# Code style
black app/ tests/
flake8 app/ tests/
```

## Testing

The test suite covers:

- Unit tests for domain models and services
- Integration tests for API endpoints
- Security validation (auth, rate limiting, headers)
- Repository operations
- Match scoring algorithms

Current coverage: **74%** (enforced minimum: 70%)

Run specific test categories:

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Security tests
pytest tests/integration/test_security_features.py
```

## Security

### Authentication Flow

1. User registers with email + password → backend derives username from email local-part
2. Password hashed with bcrypt (cost factor 12)
3. JWT access token issued (30min expiry) + refresh token (30 days)
4. Refresh token stored in DB with revocation support
5. Access token sent via `Authorization: Bearer <token>` header
6. Refresh endpoint swaps old refresh token for new pair (rotation)

### Best Practices

- Store `JWT_SECRET` and `REFRESH_SECRET` in environment variables or secret managers
- Use HTTPS in production (HSTS enforces this)
- Enable Redis for distributed rate limiting across multiple instances
- Rotate secrets periodically
- Monitor structured logs for correlation ID-based request tracing

### Known Limitations

- Username field still required in DB schema (derived automatically, migration pending)
- Refresh token cleanup job not implemented (manual revocation only)
- No role-based access control (single-user system currently)

## Performance

Benchmarks on modest hardware (Intel i5, 8GB RAM):

| Operation | Mean Latency | P95 Latency |
|-----------|--------------|-------------|
| Match Calculation | <1ms | <1ms |
| Resume Generation | 125ms | 142ms |
| ATS Report | 133ms | 151ms |

**Optimization Notes**:
- Document generation is CPU-bound (template rendering)
- Match scoring is fast due to in-memory computation
- Future: Add caching layer for generated documents
- Future: Async job queue for batch operations

## Roadmap

### Planned Features

- [ ] PDF resume export via ReportLab or WeasyPrint
- [ ] Job scraping integrations (LinkedIn, Indeed)
- [ ] Email notifications for application deadlines
- [ ] Advanced analytics dashboard (application funnel, success rates)
- [ ] Multi-user support with team collaboration
- [ ] Mobile app (React Native or Flutter)
- [ ] AI-powered cover letter generation
- [ ] Calendar integration for interview scheduling

### Technical Debt

- [ ] Migrate username column to nullable in DB schema
- [ ] Add background task queue (Celery or arq)
- [ ] Implement token cleanup cron job
- [ ] Add Prometheus metrics endpoint
- [ ] Dockerize application with compose for Redis + API
- [ ] Add OpenAPI schema validation tests
- [ ] Improve error messages in GUI (user-friendly wording)

## Contributing

I welcome contributions, bug reports, and feature requests. Here's how to get involved:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with descriptive commits
4. Add tests for new functionality
5. Ensure all tests pass and coverage stays above 70%
6. Submit a pull request with a clear description

**Coding Standards**:
- Follow PEP 8 style guide
- Add docstrings to all public functions
- Use type hints for function signatures
- Keep functions focused (single responsibility)
- Write tests before pushing

## Support This Project

If Unicorn Hunter Pro has helped you land your dream job or saved you hours of manual tracking, consider supporting its development. This project is free and open source, built in my spare time to solve a problem I personally faced during job hunting.

Your donations help me:
- Add new features and integrations
- Maintain dependencies and security updates
- Improve documentation and tutorials
- Cover hosting costs for demo instances

**Donation Options**:

- **Buy Me a Coffee**: [buymeacoffee.com/arielk](https://buymeacoffee.com/arielk)
- **Ko-fi**: [ko-fi.com/arielk](https://ko-fi.com/arielk)
- **PayPal**: [paypal.me/arielk3998](https://paypal.me/arielk3998)

Even a small contribution means a lot and keeps this project alive. Thank you for your support.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for personal or commercial purposes. Attribution is appreciated but not required.

---

**Built with**: FastAPI, Pydantic, SQLite, Redis, Tkinter, Jose (JWT), Passlib (bcrypt)

**Author**: Ariel K ([GitHub](https://github.com/arielk3998))

**Last Updated**: November 25, 2025

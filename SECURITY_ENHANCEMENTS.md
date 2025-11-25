# Resume Toolkit API - Security & Infrastructure Enhancements

## 🚀 Latest Updates (November 25, 2025)

### Advanced Security & Scaling Features

#### 1. Redis-Backed Rate Limiting
- **Multi-instance scaling**: Rate limits persist across app instances via Redis
- **Automatic fallback**: Uses in-memory storage when Redis unavailable
- **Configuration**: Set `REDIS_URL` and `RATE_LIMIT_RPM` environment variables
- **Location**: `app/infrastructure/cache/redis_rate_limiter.py`

```bash
# Enable Redis rate limiting
export REDIS_URL=redis://localhost:6379/0
export RATE_LIMIT_RPM=100
```

#### 2. Structured Logging with Correlation IDs
- **JSON logs**: Machine-parseable structured logs
- **Request tracking**: Unique correlation ID per request
- **Header support**: Clients can pass `X-Correlation-ID` or auto-generated
- **Location**: `app/infrastructure/logging/structured_logger.py`

```bash
# Configure logging
export LOG_LEVEL=INFO
export STRUCTURED_LOGS=true
```

Example log output:
```json
{
  "timestamp": "2025-11-25T19:45:42.732Z",
  "level": "INFO",
  "logger": "app.presentation.api.main",
  "message": "FastAPI application configured successfully",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 3. User Management & Refresh Tokens
- **JWT access tokens**: Short-lived (30 min) for API access
- **Refresh tokens**: Long-lived (30 days) for token renewal
- **Token rotation**: New refresh token issued on each refresh
- **Secure storage**: Bcrypt password hashing, SQLite token storage
- **Location**: `app/application/services/user_service.py`

**New Endpoints:**
- `POST /auth/register` - Create account
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Revoke refresh token

```bash
# Example: Register user
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "secure123"}'

# Response
{
  "access_token": "eyJhbGc...",
  "refresh_token": "d_8fh3j...",
  "token_type": "bearer"
}
```

#### 4. Enhanced Security Headers
- **CSP (Content Security Policy)**: Configurable via `CSP_POLICY`
- **HSTS (Strict Transport Security)**: Enabled when `HTTPS_ENABLED=true`
- **Additional headers**: X-Frame-Options, X-Content-Type-Options, etc.

```bash
# Enable HTTPS-specific headers
export HTTPS_ENABLED=true
export HSTS_MAX_AGE=31536000
export CSP_POLICY="default-src 'self'; script-src 'self'"
```

### Environment Variables Reference

```bash
# Security
API_KEY=your-api-key-here                    # Optional API key auth
JWT_SECRET=your-jwt-secret                   # JWT signing secret
REFRESH_SECRET=your-refresh-secret           # Refresh token secret

# Rate Limiting
REDIS_URL=redis://localhost:6379/0           # Redis connection
RATE_LIMIT_RPM=100                           # Requests per minute

# Logging
LOG_LEVEL=INFO                               # DEBUG|INFO|WARNING|ERROR
STRUCTURED_LOGS=true                         # JSON logs enabled

# HTTPS Security
HTTPS_ENABLED=true                           # Enable HSTS
HSTS_MAX_AGE=31536000                        # HSTS max-age (1 year)
CSP_POLICY=default-src 'self'                # Content Security Policy

# Database
DATABASE_PATH=data/resume_toolkit.db         # SQLite database path
```

### Running the Application

```bash
# Activate virtual environment
& "D:/Master Folder/Ariel's/Personal Documents/.venv/Scripts/Activate.ps1"

# Install new dependencies
pip install redis

# Start the server
uvicorn app.presentation.api.main:app --host 127.0.0.1 --port 8001 --log-level info
```

**Server is now running at:** http://127.0.0.1:8001
- **API Documentation**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

### Testing Security Features

```bash
# Test rate limiting (will succeed first N times, then 429)
for i in {1..15}; do curl http://127.0.0.1:8001/health; done

# Test correlation ID tracking
curl -H "X-Correlation-ID: test-123" http://127.0.0.1:8001/health -v
# Response will include: X-Correlation-ID: test-123

# Test user registration
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"pass123"}'

# Test login
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

### Architecture Updates

**New Components:**
- `app/infrastructure/cache/` - Redis rate limiting
- `app/infrastructure/logging/` - Structured logging
- `app/infrastructure/database/sqlite_user_repo.py` - User storage
- `app/application/services/user_service.py` - Auth logic
- `app/presentation/api/routers/auth_router.py` - Auth endpoints

**Performance Metrics** (from profiling script):
- MatchingEngine: ~0.00ms avg per call
- Resume generation: ~125ms avg (P95: 144ms)
- ATS report: ~133ms avg (P95: 165ms)

### Test Coverage: 74%

All tests passing with enhanced security features integrated.

---

## Previous Features (Already Implemented)

- ✅ 8-Factor matching algorithm
- ✅ Profile, Job, Application, Document CRUD
- ✅ Analytics endpoints
- ✅ Event-driven architecture
- ✅ Pydantic v2 models
- ✅ ATS report generation
- ✅ API key + JWT authentication
- ✅ Performance profiling script
- ✅ CI/CD with coverage enforcement

```markdown
# Security Hardening Documentation

## Overview

This document outlines the security measures implemented in the Document Filler web application to protect against common vulnerabilities and ensure data security.

## Security Features Implemented

### 1. Input Validation and Sanitization ✅

**Location:** `backend/app/utils/validation.py`

#### File Upload Security
- **Filename sanitization**: Prevents directory traversal attacks
  - Removes path components (`../`, `./`, etc.)
  - Validates filename characters (alphanumeric + safe symbols only)
  - Enforces maximum filename length (255 characters)
  - Blocks null bytes

- **File type validation**: Multi-layer approach
  - Extension validation (.docx only)
  - MIME type validation (using python-magic)
  - File size limits (50MB max)
  - Empty file detection

- **Implementation:**
  ```python
  InputValidator.sanitize_filename(filename)  # Safe filename
  InputValidator.validate_file_upload(path, ['.docx'])  # Deep validation
  ```

#### Text Content Sanitization
- **XSS Prevention**:
  - HTML entity escaping for all user inputs
  - Dangerous pattern detection (<script>, javascript:, event handlers)
  - Content length limits
  - Null byte removal

- **Prompt Injection Prevention**:
  - Detects suspicious patterns ("ignore previous instructions", etc.)
  - Validates prompt length (max 50,000 characters)
  - Sanitizes AI-generated content

- **Implementation:**
  ```python
  InputValidator.sanitize_text(text, max_length)
  ContentSanitizer.sanitize_prompt(prompt)
  ContentSanitizer.sanitize_ai_response(content)
  ```

#### ID Validation
- **Document/Section IDs**: UUID format validation
- **URL Validation**: Protocol and SSRF prevention
- **Prevents** injection attacks through IDs

### 2. Database Encryption ✅

**Location:** `backend/app/utils/encryption.py`, `backend/app/models/database.py`

#### Encrypted Fields
Using Fernet (symmetric encryption) with PBKDF2 key derivation:

- **File paths**: Encrypted in database
- **API keys**: Encrypted storage
- **Configuration values**: Sensitive settings encrypted
- **User credentials**: Passwords hashed with PBKDF2+salt

#### Implementation
```python
# SQLAlchemy encrypted field type
class EncryptedString(TypeDecorator):
    # Automatically encrypts on write, decrypts on read

# Usage in models
file_path = Column(EncryptedString(500))
api_key = Column(EncryptedString(255))
```

#### Encryption Details
- **Algorithm**: Fernet (AES-128 in CBC mode with HMAC)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Key Storage**: Derived from SECRET_KEY in environment

#### Password Hashing
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Salt**: 16 bytes random (per password)
- **Iterations**: 100,000
- **Storage Format**: `salt:hash`

### 3. Rate Limiting ✅

**Location:** `backend/app/utils/security.py`

#### Endpoint-Specific Limits
- **Content Generation**: 10 requests/minute per IP
- **Document Upload**: 5 requests/minute per IP
- **Review/Analysis**: 10 requests/minute per IP
- **General API**: 100 requests/minute per IP

#### Implementation
```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    # Tracks requests per IP address
    # Configurable windows and limits
    # Returns HTTP 429 when exceeded
```

#### Benefits
- **DDoS Protection**: Prevents resource exhaustion
- **API Abuse Prevention**: Limits automated requests
- **Fair Usage**: Ensures availability for all users

### 4. Security Headers ✅

**Location:** `backend/app/utils/security.py`

#### Headers Applied
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### Protection Provided
- **XSS**: Content sniffing and script injection prevention
- **Clickjacking**: Frame-Options prevents embedding
- **HTTPS Enforcement**: HSTS header
- **CSP**: Restricts resource loading
- **Privacy**: Referrer policy limits information leakage

### 5. Request Validation ✅

**Location:** `backend/app/utils/security.py`

#### Suspicious Pattern Detection
Blocks requests containing:
- Directory traversal (`..`)
- Null bytes (`%00`)
- XSS attempts (`<script`)
- JavaScript protocol (`javascript:`)
- SQL injection patterns (`union select`)
- Command injection (`exec(`)

#### Request Size Limits
- **Maximum size**: 50MB
- **Returns**: HTTP 413 for oversized requests

### 6. CSRF Protection ✅

**Location:** `backend/app/utils/security.py`

#### Token-Based Protection
- **Token Generation**: Secure random tokens (32 bytes)
- **Lifetime**: 1 hour
- **One-Time Use**: Tokens consumed on validation
- **Auto-Cleanup**: Expired tokens removed

#### Implementation
```python
csrf = CSRFProtection()
token = csrf.generate_token()  # Generate for forms
csrf.validate_token(token)  # Validate on submission
```

### 7. Authentication & Authorization 🚧

**Location:** `backend/app/utils/security.py`, `backend/app/models/database.py`

#### JWT-Based Authentication (Ready to Enable)
- **Token Type**: JWT (JSON Web Tokens)
- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Storage**: Bearer token in Authorization header

#### User Model
```python
class User(Base):
    username: str
    email: str
    hashed_password: str  # PBKDF2
    is_active: bool
    is_admin: bool
```

#### API Key Support
- **Per-User Keys**: Multiple keys per user
- **Key Hashing**: SHA-256
- **Expiration**: Optional expiry dates
- **Tracking**: Last used timestamp
- **Revocation**: Can be deactivated

#### To Enable Authentication
1. Uncomment auth routes in `main.py`
2. Add login/register endpoints
3. Apply `@requires_auth` decorator to protected routes
4. Initialize database with `db.create_tables()`

### 8. Audit Logging ✅

**Location:** `backend/app/models/database.py`

#### Logged Events
```python
class AuditLog(Base):
    user_id: int
    action: str  # document_upload, content_generate, etc.
    resource_type: str  # document, api_key, etc.
    resource_id: str
    ip_address: str
    user_agent: str
    status: str  # success, failure, error
    details: JSON
    timestamp: datetime
```

#### Use Cases
- **Security Monitoring**: Track unauthorized access attempts
- **Compliance**: Audit trail for data access
- **Debugging**: Trace user actions
- **Analytics**: Usage patterns

## Security Best Practices

### For Deployment

#### 1. Environment Variables
```bash
# MUST change these in production:
SECRET_KEY=<generate-strong-random-key>
OPENWEBUI_API_KEY=<actual-api-key>
DATABASE_URL=<production-database>

# Recommendations:
- 32+ character random SECRET_KEY
- Use environment-specific .env files
- Never commit .env to version control
```

#### 2. HTTPS/TLS
- **Always use HTTPS** in production
- **Configure TLS certificates** (Let's Encrypt recommended)
- **Redirect HTTP to HTTPS**
- **HSTS header** already configured

#### 3. Database Security
```bash
# For production, use PostgreSQL instead of SQLite:
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Benefits:
- Better concurrent access
- Proper user permissions
- Connection encryption
- Backup capabilities
```

#### 4. API Key Management
```python
# Rotate SECRET_KEY periodically
# Use separate keys for different environments
# Store keys in secure vault (HashiCorp Vault, AWS Secrets Manager)
```

#### 5. CORS Configuration
```python
# Restrict to actual domain in production:
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# DO NOT use "*" in production
```

#### 6. Rate Limiting
```python
# Consider using Redis for distributed rate limiting:
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# More scalable than in-memory tracking
```

### For Development

#### 1. Dependency Updates
```bash
# Regular security updates:
pip list --outdated
pip install --upgrade <package>

# Or use:
pip-audit  # Checks for known vulnerabilities
```

#### 2. Code Security Scanning
```bash
# Static analysis:
bandit -r backend/  # Python security linter
semgrep --config=auto backend/  # Multi-language

# Dependency scanning:
safety check  # Check dependencies
```

#### 3. Testing
```python
# Security test cases:
- Test file upload with malicious files
- Test XSS payloads in text inputs
- Test SQL injection in queries
- Test authentication bypass
- Test rate limiting
```

## Vulnerability Assessment

### Mitigated Risks

| Vulnerability | Risk Level | Mitigation | Status |
|---------------|------------|------------|--------|
| **SQL Injection** | High | SQLAlchemy ORM, parameterized queries | ✅ Mitigated |
| **XSS** | High | Input sanitization, HTML escaping | ✅ Mitigated |
| **CSRF** | Medium | CSRF tokens | ✅ Mitigated |
| **File Upload Attacks** | High | Extension, MIME, size validation | ✅ Mitigated |
| **Directory Traversal** | High | Path sanitization | ✅ Mitigated |
| **DDoS** | Medium | Rate limiting | ✅ Mitigated |
| **Sensitive Data Exposure** | High | Database encryption | ✅ Mitigated |
| **Broken Authentication** | High | JWT, password hashing | 🚧 Ready (disabled) |
| **Security Misconfiguration** | Medium | Security headers, CSP | ✅ Mitigated |
| **Insufficient Logging** | Low | Audit logs | ✅ Mitigated |

### Remaining Considerations

#### 1. Authentication (Currently Disabled)
**Status**: Infrastructure ready, needs to be enabled

**To Enable:**
1. Create admin user
2. Add login/register endpoints
3. Protect routes with `@requires_auth`
4. Update frontend for auth flow

**Why Disabled:**
- Allows easier initial setup/testing
- Can be enabled when multi-user needed
- Single-user deployments may not need it

#### 2. Rate Limiting Storage
**Current**: In-memory (lost on restart)
**Recommended**: Redis for production
**Impact**: Better scalability, persistent tracking

#### 3. Input Sanitization Libraries
**Current**: Custom implementation
**Recommended**: Add `bleach` for HTML sanitization
**Status**: bleach added to requirements

## Security Checklist

### Before Production Deployment

- [ ] Change SECRET_KEY to strong random value
- [ ] Enable HTTPS/TLS with valid certificates
- [ ] Switch from SQLite to PostgreSQL
- [ ] Update CORS_ORIGINS to actual domains
- [ ] Enable authentication (if multi-user)
- [ ] Set up automated backups
- [ ] Configure proper logging
- [ ] Set up monitoring/alerting
- [ ] Run security scan (bandit, semgrep)
- [ ] Update all dependencies
- [ ] Review and restrict API permissions
- [ ] Test rate limiting
- [ ] Verify file upload restrictions
- [ ] Test input validation
- [ ] Configure firewall rules
- [ ] Set up intrusion detection
- [ ] Document incident response plan

### Regular Maintenance

- [ ] Weekly dependency updates
- [ ] Monthly security scans
- [ ] Quarterly penetration testing
- [ ] Review audit logs regularly
- [ ] Rotate SECRET_KEY every 90 days
- [ ] Review and update rate limits
- [ ] Check for new OWASP Top 10 vulnerabilities
- [ ] Update security documentation

## Incident Response

### If Security Breach Detected

1. **Immediate Actions**:
   - Isolate affected systems
   - Change all credentials (SECRET_KEY, API keys, passwords)
   - Review audit logs
   - Identify breach vector

2. **Investigation**:
   - Check `audit_logs` table for suspicious activity
   - Review application logs
   - Identify compromised data
   - Determine breach timeline

3. **Remediation**:
   - Patch vulnerability
   - Restore from clean backup if needed
   - Force password resets for affected users
   - Revoke compromised API keys

4. **Post-Incident**:
   - Document findings
   - Update security measures
   - Notify affected parties (if required by law)
   - Conduct security review

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email security details to [maintainer email]
3. Include:
   - Vulnerability description
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [Cryptography Documentation](https://cryptography.io/)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-22 | Initial security implementation |
|  |  | - Input validation |
|  |  | - Database encryption |
|  |  | - Rate limiting |
|  |  | - Security headers |
|  |  | - CSRF protection |
|  |  | - Audit logging |

---

**Last Updated**: 2025-11-22
**Security Contact**: [To be configured]
**Next Security Review**: [To be scheduled]
```

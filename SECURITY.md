# Security Guide

## 🔐 Security Considerations for Production

This demo application includes mock data and basic security. For production deployment, implement these measures:

## 1. Data Encryption

### Sensitive Data at Rest

```python
# Use Fernet encryption (symmetric)
from cryptography.fernet import Fernet

# Generate key (store in secure key management system)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt payment info
encrypted_card = cipher.encrypt(b"4111111111111111")

# Decrypt when needed
decrypted_card = cipher.decrypt(encrypted_card)
```

### Sensitive Data in Transit
- Use HTTPS/TLS for all communications
- Never send unencrypted credit cards, passports, or PII
- Use API keys with proper scoping

### Key Management
- **Development**: Environment variables
- **Production**: Use a Key Management Service
  - AWS KMS
  - Azure Key Vault
  - HashiCorp Vault
  - Google Cloud KMS

## 2. Authentication & Authorization

### User Authentication
```python
# Recommended: OAuth 2.0 / OIDC
from authlib.integrations.flask_client import OAuth

# Options:
# - Corporate SSO (Okta, Auth0, Azure AD)
# - SAML 2.0 for enterprise
# - Multi-factor authentication (MFA)
```

### Role-Based Access Control (RBAC)
```python
roles = {
    "employee": ["view_policy", "book_travel", "view_own_trips"],
    "manager": ["view_policy", "book_travel", "view_own_trips", "approve_trips"],
    "admin": ["*"]  # Full access
}
```

## 3. Secure Payment Processing

### PCI-DSS Compliance

**DO NOT store:**
- Full credit card numbers (PAN)
- CVV/CVC codes
- Unencrypted card data

**DO store:**
- Tokenized card references
- Last 4 digits for display
- Encrypted data with proper KMS

### Payment Gateway Integration
```python
# Use payment processors (they handle PCI compliance)
# - Stripe
# - Braintree
# - Adyen
# - Corporate travel payment systems

import stripe
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

# Create payment intent (server-side)
payment_intent = stripe.PaymentIntent.create(
    amount=150000,  # in cents
    currency="usd",
    payment_method_types=["card"],
)
```

## 4. Secure LLM Operations

### Ollama Security

**Network Isolation:**
```bash
# Run Ollama on isolated network
# Don't expose port 11434 to internet
# Use firewall rules

# Good: localhost only
ollama serve --host 127.0.0.1

# Bad: exposed to internet
ollama serve --host 0.0.0.0  # DON'T DO THIS
```

**Prompt Injection Protection:**
```python
def sanitize_user_input(text: str) -> str:
    """Prevent prompt injection attacks"""
    # Remove system prompts
    text = text.replace("system:", "")
    text = text.replace("assistant:", "")
    
    # Limit length
    max_length = 500
    text = text[:max_length]
    
    # Escape special characters
    import html
    text = html.escape(text)
    
    return text
```

**Data Privacy:**
- Never send PII to cloud LLMs without encryption
- Use local Ollama for sensitive data
- Implement data loss prevention (DLP)
- Log all LLM interactions for audit

## 5. Database Security

### Connection Security
```python
# Use SSL for database connections
import psycopg2

conn = psycopg2.connect(
    host="db.example.com",
    database="travel_db",
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    sslmode="require",  # Enforce SSL
    sslrootcert="/path/to/ca-cert"
)
```

### SQL Injection Prevention
```python
# ALWAYS use parameterized queries
cursor.execute(
    "SELECT * FROM bookings WHERE user_id = %s",
    (user_id,)  # Parameterized
)

# NEVER use string formatting
# cursor.execute(f"SELECT * FROM bookings WHERE user_id = {user_id}")  # DANGEROUS
```

### Encryption at Rest
- Use encrypted database storage
- Encrypt backups
- Implement column-level encryption for sensitive fields

## 6. API Security

### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["100 per hour"],
    storage_uri="redis://localhost:6379"
)

@app.route("/api/search")
@limiter.limit("20 per minute")
def search_flights():
    pass
```

### API Key Management
```python
# Store API keys securely
# - Never commit to git
# - Use environment variables
# - Rotate regularly
# - Use separate keys for dev/staging/prod

import os
api_key = os.environ.get("AMADEUS_API_KEY")
if not api_key:
    raise ValueError("API key not configured")
```

### Input Validation
```python
from pydantic import BaseModel, validator
from datetime import datetime

class TripRequest(BaseModel):
    origin: str
    destination: str
    depart_date: datetime
    budget: float
    
    @validator('budget')
    def budget_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Budget must be positive')
        if v > 50000:
            raise ValueError('Budget exceeds maximum')
        return v
    
    @validator('origin', 'destination')
    def validate_airport_code(cls, v):
        if not v.isalpha() or len(v) != 3:
            raise ValueError('Invalid airport code')
        return v.upper()
```

## 7. Audit Logging

### Log All Security Events
```python
import logging
from datetime import datetime

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

handler = logging.FileHandler('audit.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s'
))
audit_logger.addHandler(handler)

# Log security events
def log_booking(user_id, booking_details):
    audit_logger.info(
        f"BOOKING | User: {user_id} | "
        f"Destination: {booking_details['destination']} | "
        f"Cost: ${booking_details['total_cost']}"
    )

def log_policy_violation(user_id, violation):
    audit_logger.warning(
        f"POLICY_VIOLATION | User: {user_id} | "
        f"Violation: {violation}"
    )

def log_auth_failure(user_id, ip_address):
    audit_logger.error(
        f"AUTH_FAILURE | User: {user_id} | IP: {ip_address}"
    )
```

### What to Log
- ✅ Authentication attempts (success/failure)
- ✅ Booking transactions
- ✅ Policy violations
- ✅ Data access (especially sensitive data)
- ✅ Configuration changes
- ✅ API calls to external services
- ❌ Never log passwords, credit cards, or PII in plaintext

## 8. Secure Configuration

### Environment Variables
```bash
# .env file (never commit to git)
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=postgresql://user:pass@localhost/traveldb
STRIPE_SECRET_KEY=sk_live_xxxxx
JWT_SECRET_KEY=your-super-secret-key

# Encryption keys (use KMS in production)
ENCRYPTION_KEY=your-fernet-key

# API credentials
AMADEUS_API_KEY=xxxxx
AMADEUS_API_SECRET=xxxxx
```

### .gitignore
```
# Never commit these files
.env
.env.local
*.key
*.pem
config/secrets.json
data/travel_profile.json  # Contains sensitive data
data/booking_history.json
```

### Secrets Management in Production
```python
# AWS Secrets Manager
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

stripe_key = get_secret('travel-app/stripe-key')
```

## 9. Compliance

### GDPR (EU)
- Implement right to erasure (delete user data)
- Data portability (export user data)
- Consent management
- Data processing agreements with vendors

### CCPA (California)
- Right to know what data is collected
- Right to delete personal data
- Opt-out of data selling

### PCI-DSS (Payment Cards)
- Never store full PANs
- Use tokenization
- Maintain secure network
- Regular security testing

### SOX (if public company)
- Financial reporting controls
- Audit trails for all transactions
- Access controls and segregation of duties

## 10. Incident Response Plan

### When a Breach Occurs

1. **Contain**: Isolate affected systems
2. **Assess**: Determine scope of breach
3. **Notify**: Inform affected users within 72 hours (GDPR)
4. **Remediate**: Fix vulnerability
5. **Document**: Complete incident report
6. **Review**: Update security practices

### Incident Response Team
- Security Lead
- Engineering Lead
- Legal Counsel
- Communications/PR
- External Security Consultant

## 11. Security Checklist

### Before Production Launch

- [ ] Enable HTTPS/TLS everywhere
- [ ] Implement authentication & authorization
- [ ] Encrypt sensitive data (at rest & in transit)
- [ ] Use secrets manager (not environment variables)
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] Regular dependency updates
- [ ] Penetration testing
- [ ] Security training for developers
- [ ] Incident response plan
- [ ] Compliance review (GDPR, PCI-DSS, etc.)

### Ongoing Security

- [ ] Monthly security patches
- [ ] Quarterly penetration testing
- [ ] Annual security audit
- [ ] Regular backup testing
- [ ] Access review (remove old accounts)
- [ ] Log monitoring & alerting
- [ ] Vulnerability scanning

## 12. Secure Development Practices

### Code Review Checklist
```
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Parameterized queries used
- [ ] Proper error handling (no stack traces to user)
- [ ] Authentication checks on all endpoints
- [ ] Authorization checks (RBAC)
- [ ] Sensitive data encrypted
- [ ] Audit logging added
- [ ] Rate limiting implemented
- [ ] Dependencies up to date
```

### Git Security
```bash
# Pre-commit hook to prevent secrets
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline

# Add to .git/hooks/pre-commit
#!/bin/bash
detect-secrets scan --baseline .secrets.baseline
if [ $? -ne 0 ]; then
    echo "⚠️  Possible secrets detected! Commit blocked."
    exit 1
fi
```

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [GDPR Official Text](https://gdpr.eu/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## 🚨 Report Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email: security@yourcompany.com
3. Include details: steps to reproduce, impact
4. Allow 90 days for remediation before disclosure

---

**Remember**: Security is not a feature, it's a process. Continuously review and improve your security posture.


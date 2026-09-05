# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in UPI, please **do not** open a public GitHub issue. Instead, please email the maintainers privately with:

1. Description of the vulnerability
2. Affected component (e.g., `src/upi/validation.py`)
3. Steps to reproduce
4. Potential impact
5. Suggested fix (if applicable)

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Security Considerations

### Input Validation

All numeric inputs in physics functions are validated:
- ✓ NaN rejection
- ✓ Infinity rejection
- ✓ Sign validation
- ✓ Range bounds checking

### JSON Schema Validation

- ✓ Unknown status labels rejected
- ✓ Missing required fields detected
- ✓ Bridges without relation types rejected
- ✓ STOP nodes without `stop_reason` rejected

### Credentials and access control

- Public reads and contributions do not require a login.
- EST promotion requires the shared `UPI_REVIEW_TOKEN` environment value.
- The token is read at startup, compared with `X-UPI-Review-Token`, and has no
  built-in expiry or per-user identity. An empty value disables promotion.
- `.env` is ignored by Git; database examples and Docker Compose contain
  development credentials, which must be replaced for a deployed database.
- The built-in server uses HTTP. Use HTTPS termination for remote review-token
  requests. Database connection strings are not printed by server startup.

### Known Limitations

- Package version is declared in `pyproject.toml`.
- Do not rely on this for critical decision-making
- Always verify against original scientific literature
- Use in research and educational contexts only

## Dependency Security

Dependencies are minimal to reduce attack surface:
- `jsonschema` — For JSON validation only

Runtime extras:

- optional PostgreSQL via `psycopg` when `UPI_DATABASE_URL` is set
- optional HTTP contribution UI (`upi serve`)

The live API rejects public EST, limits POST rate, and treats indexed text as
untrusted data. Maintainer EST promotion requires `UPI_REVIEW_TOKEN`. This is
access control, not scientific verification.

## Compliance

- MIT License
- No usage restrictions
- Open for security audits
- Community-driven improvements welcome

## Version Support

Security patches are provided for:
- Latest release (current)
- Previous release (6 months)

Older versions should be upgraded to the latest stable release.

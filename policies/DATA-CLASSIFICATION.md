# Data Classification & Handling Policy

> Internal policy — applies to all services that process customer data.
> Aligned with GDPR Art. 32 and internal control framework v3.2.

## DATA-CLS-01 — Classification levels

| Level | Examples | Allowed sinks |
|-------|----------|---------------|
| Public | Marketing copy, OSS docs | any |
| Internal | Service topology, runbooks | internal wiki, Git |
| Confidential | Aggregated balances, KYC status | encrypted stores only |
| Restricted (PII) | IBAN, PAN, CVV, DOB, full name+address | encrypted stores + masked in logs |

## DATA-CLS-02 — Prohibited persistence

The following MUST NEVER be persisted to disk in plaintext, including
application logs, stdout/stderr, crash dumps, or stack traces:

- Card number (PAN), CVV, expiry
- Full IBAN (more than first 4 + last 4 characters)
- Government identifiers (BSN, SSN, passport number)
- Authentication credentials of any kind

## DATA-CLS-03 — Logging of account identifiers

Account numbers (IBAN, PAN) MUST be **masked** in any log sink. Use the shared
`mask_iban()` / `mask_pan()` helpers. The first 4 and last 4 characters MAY be
retained; everything in between MUST be replaced with `*`.

**Non-compliant:** `logger.info("charge for %s", customer.iban)`
**Compliant:**    `logger.info("charge for %s", mask_iban(customer.iban))`

## DATA-CLS-04 — Transport security

All endpoints handling Confidential or Restricted data MUST use TLS 1.2+.
Certificate verification MUST NOT be disabled (`verify=False`,
`InsecureSkipVerify`, `rejectUnauthorized: false` are all forbidden).

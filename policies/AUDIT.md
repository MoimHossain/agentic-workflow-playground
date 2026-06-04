# Audit Logging Policy

## AUDIT-01 — Mandatory audit events

Any state-changing operation in scope of MiFID II / PSD2 MUST emit an audit
event via the shared `audit.emit(event_name, actor, target, outcome)` API.

In-scope operations include:

- Money movement (charge, refund, transfer, reversal)
- KYC status changes
- Role / permission changes
- Consent grants and revocations
- Customer data exports

## AUDIT-02 — Tamper resistance

Audit events MUST be written to the append-only audit sink, not the general
application log. Direct file writes to the audit sink are forbidden — always
go through `audit.emit`.

## AUDIT-03 — DORA third-party traceability

Calls to third-party / SaaS dependencies handling Confidential or Restricted
data MUST be wrapped in `third_party.call(provider, op)` so the DORA register
can track them.

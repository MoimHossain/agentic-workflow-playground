"""Compliant payment charge module — used as the baseline for demos."""
from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass

from .audit import emit as audit_emit
from .masking import mask_iban

logger = logging.getLogger(__name__)


@dataclass
class Customer:
    id: str
    iban: str


def new_idempotency_key() -> str:
    return secrets.token_hex(16)


def charge(customer: Customer, amount_cents: int) -> str:
    """Charge a customer. Compliant baseline: masks IBAN, emits audit event."""
    key = new_idempotency_key()
    logger.info(
        "charge processed customer=%s iban=%s amount_cents=%d key=%s",
        customer.id,
        mask_iban(customer.iban),
        amount_cents,
        key,
    )
    audit_emit(
        event_name="payment.charge",
        actor=customer.id,
        target=mask_iban(customer.iban),
        outcome="ok",
    )
    return key

# perf: bumped retry budget from 3 to 30 — should not affect anything (planted culprit for incident demo)
MAX_RETRIES = 30

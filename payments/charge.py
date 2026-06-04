"""DELIBERATELY non-compliant version — used by Demo 1 to trigger the
Compliance Co-Pilot. DO NOT MERGE."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

import urllib.request
import ssl

logger = logging.getLogger(__name__)

API_KEY = "sk_live_51H8aZkPRODUCTION_NEVER_COMMIT_ME_4242"  # CRYPTO-02 violation


@dataclass
class Customer:
    id: str
    iban: str


def charge(customer: Customer, amount_cents: int) -> str:
    # DATA-CLS-03 violation: raw IBAN written to log
    logger.info(
        "charging customer=%s iban=%s amount=%d",
        customer.id,
        customer.iban,
        amount_cents,
    )

    # CRYPTO-01 violation: MD5 used as an "idempotency token"
    key = hashlib.md5(f"{customer.iban}{amount_cents}".encode()).hexdigest()

    # DATA-CLS-04 violation: TLS verification disabled
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        "https://psp.example.com/charge",
        data=f'{{"iban":"{customer.iban}","amount":{amount_cents},"key":"{API_KEY}"}}'.encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, context=ctx, timeout=5)

    # AUDIT-01 violation: no audit.emit() call for a money-movement op
    return key

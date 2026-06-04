def mask_iban(iban: str) -> str:
    """Mask middle of an IBAN, keeping the first 4 and last 4 chars."""
    if not iban or len(iban) <= 8:
        return "*" * len(iban or "")
    return iban[:4] + "*" * (len(iban) - 8) + iban[-4:]


def mask_pan(pan: str) -> str:
    digits = "".join(c for c in pan if c.isdigit())
    if len(digits) <= 8:
        return "*" * len(digits)
    return digits[:4] + "*" * (len(digits) - 8) + digits[-4:]

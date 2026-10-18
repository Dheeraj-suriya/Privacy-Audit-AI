"""Input validation utilities."""
import re
from typing import Optional

def mask_email(email: str) -> str:
    """Mask an email address for display."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """Mask a phone number."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]

def mask_aadhaar(aadhaar: str) -> str:
    """Mask an Aadhaar-like number."""
    digits = re.sub(r"\D", "", aadhaar)
    if len(digits) != 12:
        return "****"
    return "XXXX-XXXX-" + digits[-4:]

def mask_pan(pan: str) -> str:
    """Mask a PAN-like identifier."""
    pan = pan.upper().strip()
    if len(pan) != 10:
        return "****"
    return pan[:2] + "******" + pan[-2:]

def mask_generic(value: str, visible_chars: int = 4) -> str:
    """Generic masking: show last N chars."""
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]

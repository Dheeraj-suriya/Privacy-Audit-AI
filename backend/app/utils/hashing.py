"""Hashing utilities."""
import hashlib
import secrets

def generate_random_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)

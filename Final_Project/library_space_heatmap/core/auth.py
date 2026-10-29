"""Demo credential store.

PROTOTYPE ONLY: replace with your real authentication service / database.
Passwords are stored as SHA-256 hashes so they are not sitting in plain text.
"""
import hashlib
import hmac
import re

STUDENT_NUMBER_LENGTH = 7
STUDENT_NUMBER_PATTERN = re.compile(r"^[0-9]{7}$")   # exactly 7 digits, e.g. 2024123


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


ACCOUNTS = {
    "entrance": {"entrance01": _hash("entrance123")},
    "librarian": {"librarian01": _hash("library123")},
}

ADMIN_LABELS = {"entrance": "Entrance Access", "librarian": "Librarian Access"}


def is_valid_student_number(value: str) -> bool:
    return bool(STUDENT_NUMBER_PATTERN.fullmatch(value.strip()))


def verify_admin(kind: str, username: str, password: str) -> bool:
    stored = ACCOUNTS.get(kind, {}).get(username.strip())
    return stored is not None and hmac.compare_digest(stored, _hash(password))

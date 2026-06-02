import base64
import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return f"{salt}${base64.b64encode(digest).decode('utf-8')}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, digest_b64 = hashed_password.split("$", 1)
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return secrets.compare_digest(base64.b64encode(digest).decode("utf-8"), digest_b64)

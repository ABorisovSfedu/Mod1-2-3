import hmac, hashlib
from typing import Optional

def verify_hmac_sha256(secret: str, body: bytes, header_value: Optional[str]) -> bool:
    if not header_value or not header_value.startswith("sha256="):
        return False
    got = header_value.split("=", 1)[1].strip()
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(got, expected)

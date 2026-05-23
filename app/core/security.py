import hmac
import hashlib

def sign_payload(secret: str, payload: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
def verify_signature(secret: str, payload: str, signature: str) -> bool:
    expected = sign_payload(secret, payload)
    return hmac.compare_digest(expected, signature)
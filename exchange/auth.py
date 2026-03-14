import time
import hmac
import hashlib
import base64

def sign_request(secret: str, timestamp: str, method: str, endpoint: str, body: str = "") -> str:
    """
    Genera la firma HMAC-SHA256 requerida por KuCoin.
    """
    payload = f"{timestamp}{method}{endpoint}{body}"
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

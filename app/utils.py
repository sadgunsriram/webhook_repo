import hmac
import hashlib
from flask import request
from config import Config


def verify_signature(payload):
    signature = request.headers.get("X-Hub-Signature-256")

    # If no secret configured, allow (for local testing)
    if not Config.GITHUB_SECRET:
        return True

    if signature is None:
        return False

    sha_name, signature = signature.split("=")

    mac = hmac.new(
        Config.GITHUB_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )

    return hmac.compare_digest(mac.hexdigest(), signature)
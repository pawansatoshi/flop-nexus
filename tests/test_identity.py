from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from flop_nexus.identity import verify_signed_event

BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = BASE58[r] + out
    return "1" * (len(data) - len(data.lstrip(b"\0"))) + (out or "1")


def test_verify_ed25519_did_signature() -> None:
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    did = "did:key:z" + b58encode(b"\xed\x01" + public)
    room = "lobby"
    nonce = 1
    text = "hello Nexus"
    signature = private.sign(f"{room}|{nonce}|{text}".encode()).hex()

    # The production API expects base64url, so convert the test signature.
    import base64
    signature = base64.urlsafe_b64encode(bytes.fromhex(signature)).decode().rstrip("=")
    assert verify_signed_event(did, room, nonce, text, signature)
    assert not verify_signed_event(did, room, nonce, "tampered", signature)

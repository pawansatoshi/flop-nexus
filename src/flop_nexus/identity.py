"""Minimal verification for public Technocore did:key Ed25519 identities."""

from __future__ import annotations

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_ED25519_MULTICODEC = bytes((0xED, 0x01))


def _b58decode(value: str) -> bytes:
    number = 0
    for char in value:
        try:
            digit = _BASE58.index(char)
        except ValueError as exc:
            raise ValueError("invalid base58 character") from exc
        number = number * 58 + digit
    raw = number.to_bytes(max(1, (number.bit_length() + 7) // 8), "big")
    prefix = len(value) - len(value.lstrip("1"))
    return b"\x00" * prefix + (b"" if raw == b"\x00" else raw)


def public_key_from_did(did: str) -> bytes:
    if not did.startswith("did:key:z"):
        raise ValueError("only did:key base58btc identifiers are supported")
    decoded = _b58decode(did[9:])
    if not decoded.startswith(_ED25519_MULTICODEC):
        raise ValueError("DID is not an Ed25519 did:key")
    public_key = decoded[2:]
    if len(public_key) != 32:
        raise ValueError("invalid Ed25519 public key length")
    return public_key


def normalize_text(text: str) -> str:
    """Apply the single-line normalization used by the signed message lane."""
    return " ".join(text.replace("\r", "\n").splitlines()).strip()


def decode_signature(signature: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
    except ValueError as exc:
        raise ValueError("invalid base64url signature") from exc


def verify_signed_event(did: str, room: str, nonce: int, text: str, signature: str) -> bool:
    """Verify a Technocore Ed25519 signature over room|nonce|normalized-text."""
    public_key = Ed25519PublicKey.from_public_bytes(public_key_from_did(did))
    payload = f"{room}|{nonce}|{normalize_text(text)}".encode("utf-8")
    try:
        public_key.verify(decode_signature(signature), payload)
    except InvalidSignature:
        return False
    return True

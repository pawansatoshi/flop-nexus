"""Vercel ASGI entrypoint for FLOP Nexus."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flop_nexus.api import app  # noqa: E402

__all__ = ["app"]

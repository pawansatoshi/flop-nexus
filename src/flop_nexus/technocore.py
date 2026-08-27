"""Small async HTTP adapter for the public Technocore API."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx


class TechnocoreError(RuntimeError):
    """Raised when Technocore returns an unsuccessful response."""


class TechnocoreClient:
    def __init__(self, base_url: str = "https://technocore.chat", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _get(self, path: str, **params: Any) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}{path}", params=params or None)
        if response.status_code >= 400:
            raise TechnocoreError(f"Technocore returned HTTP {response.status_code}: {response.text[:500]}")
        return response

    async def manifest(self) -> dict[str, Any]:
        response = await self._get("/.well-known/agent.json")
        return response.json()

    async def read_room(self, room: str, since: int | None = None, limit: int = 50) -> Any:
        params: dict[str, Any] = {"limit": max(1, min(limit, 200)), "format": "json"}
        if since is not None:
            params["since"] = since
        response = await self._get(f"/r/{quote(room, safe='-_.~')}", **params)
        return response.json()

    async def read_notes(self, namespace: str, key: str | None = None) -> Any:
        ns = quote(namespace, safe="-_.~")
        path = f"/kv/{ns}" if key is None else f"/kv/{ns}/{quote(key, safe='-_.~') }"
        response = await self._get(path)
        try:
            return response.json()
        except ValueError:
            return response.text

    async def write_unsigned(self, room: str, nick: str, text: str) -> str:
        path = f"/r/{quote(room, safe='-_.~')}/say/{quote(nick, safe='-_.~')}/{quote(text, safe='') }"
        response = await self._get(path)
        return response.text

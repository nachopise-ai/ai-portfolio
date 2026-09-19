from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    base_url: str
    model: str
    api_key: str
    timeout_seconds: float = 20.0


class OpenAICompatibleProvider:
    """Optional adapter; it is never selected by default and never stores a key."""

    def __init__(self, config: ProviderConfig):
        if not config.base_url or not config.model or not config.api_key:
            raise ValueError("provider requires base_url, model, and API key via environment")
        self.config = config

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps(
            {
                "model": self.config.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url.rstrip('/')}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("provider request failed") from exc
        try:
            return str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("provider returned an invalid response shape") from exc

from __future__ import annotations

import re
from pathlib import PurePath


class UnsafeContentError(ValueError):
    """Raised when an input crosses a documented safety boundary."""


class UnsupportedDocumentError(ValueError):
    """Raised when a document type is not supported by the ingestion path."""


SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".pdf"}

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{12,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)

_INJECTION_PATTERNS = (
    (
        "instruction_override",
        re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    ),
    (
        "instruction_override",
        re.compile(r"ignora\s+(?:todas\s+)?las\s+instrucciones", re.IGNORECASE),
    ),
    (
        "system_prompt_exfiltration",
        re.compile(
            r"(?:reveal|show|print|muestra|revela).{0,40}(?:system prompt|prompt del sistema)",
            re.IGNORECASE,
        ),
    ),
    (
        "secret_exfiltration",
        re.compile(
            r"(?:reveal|show|print|muestra|revela).{0,40}(?:secret|secreto|api key|clave)",
            re.IGNORECASE,
        ),
    ),
    ("role_hijack", re.compile(r"you are now|ahora eres|actúa como el sistema", re.IGNORECASE)),
)


def validate_filename(filename: str) -> str:
    """Allow a simple file name and prevent path traversal."""

    cleaned = filename.strip().replace("\\", "/")
    path = PurePath(cleaned)
    if not cleaned or path.name != cleaned or path.name in {".", ".."}:
        raise UnsafeContentError("filename must be a single safe file name")
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(
            f"unsupported extension {extension or '<none>'}; use md, txt, or pdf"
        )
    return path.name


def find_secret_patterns(text: str) -> list[str]:
    """Return only stable pattern identifiers, never the matching secret."""

    return [
        name
        for name, pattern in (
            ("private_key", _SECRET_PATTERNS[0]),
            ("provider_key", _SECRET_PATTERNS[1]),
            ("github_token", _SECRET_PATTERNS[2]),
            ("aws_access_key", _SECRET_PATTERNS[3]),
        )
        if pattern.search(text)
    ]


def ensure_no_obvious_secrets(text: str) -> None:
    matches = find_secret_patterns(text)
    if matches:
        raise UnsafeContentError("document rejected because it resembles a secret")


def detect_prompt_injection(text: str) -> list[str]:
    flags: list[str] = []
    for name, pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            flags.append(name)
    return sorted(set(flags))

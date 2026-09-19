from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass

from .security import ensure_no_obvious_secrets, validate_filename


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str
    start_char: int
    end_char: int


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs).strip()


def _split_long_text(text: str, target_chars: int, overlap: int) -> list[str]:
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + target_chars)
        if end < len(text):
            boundary = max(text.rfind(".", start, end), text.rfind(";", start, end))
            if boundary > start + target_chars // 2:
                end = boundary + 1
        part = text[start:end].strip()
        if part:
            parts.append(part)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return parts


def chunk_text(text: str, target_chars: int = 900, overlap: int = 120) -> list[TextChunk]:
    if target_chars < 200:
        raise ValueError("target_chars must be at least 200")
    if overlap < 0 or overlap >= target_chars:
        raise ValueError("overlap must be non-negative and smaller than target_chars")
    normalized = normalize_text(text)
    if not normalized:
        return []

    paragraphs = [paragraph for paragraph in normalized.split("\n\n") if paragraph]
    pieces: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > target_chars:
            if current:
                pieces.append(current)
                current = ""
            pieces.extend(_split_long_text(paragraph, target_chars, overlap))
            continue
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= target_chars:
            current = candidate
        else:
            pieces.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{paragraph}".strip()
    if current:
        pieces.append(current)

    chunks: list[TextChunk] = []
    cursor = 0
    for index, piece in enumerate(pieces):
        start = normalized.find(piece.strip(), cursor)
        if start < 0:
            start = cursor
        end = start + len(piece)
        chunks.append(TextChunk(index=index, content=piece.strip(), start_char=start, end_char=end))
        cursor = max(cursor, end - overlap)
    return chunks


def extract_text(filename: str, data: bytes) -> str:
    safe_name = validate_filename(filename)
    extension = safe_name.rsplit(".", 1)[-1].lower()
    if extension in {"md", "markdown", "txt"}:
        text = data.decode("utf-8-sig")
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - dependency is declared
            raise RuntimeError("PDF support requires the declared pypdf dependency") from exc
        reader = PdfReader(io.BytesIO(data))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = normalize_text(text)
    ensure_no_obvious_secrets(normalized)
    if not normalized:
        raise ValueError("document has no extractable text")
    return normalized

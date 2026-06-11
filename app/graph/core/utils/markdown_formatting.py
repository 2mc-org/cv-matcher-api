"""Shared markdown section helpers for graph services."""

from __future__ import annotations

import re
from datetime import datetime


def markdown_heading(title: str, heading_level: int = 2) -> str:
    if not title:
        return ""
    return f"{'#' * heading_level} {title}\n\n"


def markdown_section(title: str, body: str, *, heading_level: int = 2) -> str:
    body = body.strip()
    if not body:
        return ""
    return markdown_heading(title, heading_level) + body


def markdown_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item and item.strip())


def markdown_labeled(obj: object, fields: tuple[tuple[str, str], ...]) -> str:
    lines: list[str] = []
    for key, label in fields:
        value = getattr(obj, key, None)
        if value is None or value == "" or value == []:
            continue
        lines.append(f"- **{label}**: {value}")
    return "\n".join(lines)


def normalize_markdown_headings(text: str, *, bump: int) -> str:
    return re.sub(
        r"^(#{1,2})\s",
        lambda match: "#" * min(len(match.group(1)) + bump, 6) + " ",
        text,
        flags=re.MULTILINE,
    )


def format_markdown_datetime(value: datetime) -> str:
    return value.strftime("%b %d, %Y")

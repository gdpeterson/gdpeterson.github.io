"""Shared utilities for the static-site build.

This module deliberately contains only generic file, text, URL, and image
helpers. Publication-specific logic lives in ``scripts/publications.py``.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any = None) -> Any:
    """Load UTF-8 JSON, returning *default* when the file does not exist."""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: Any) -> str:
    """Normalize small amounts of BibTeX/LaTeX-like text for display."""
    if not value:
        return ""
    text = html.unescape(str(value))
    replacements = {
        r"\\mathsemicolon": ";",
        "{": "",
        "}": "",
        "\\&": "&",
        "\\_": "_",
        "~": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def with_site_base(rendered: str, site_base: str) -> str:
    """Prefix root-relative ``href`` and ``src`` attributes for project sites."""
    if not site_base:
        return rendered
    return re.sub(
        r'(?P<attr>href|src)="/',
        rf'\g<attr>="{site_base}/',
        rendered,
    )


def validate_image_catalog(root: Path, catalog: dict[str, dict[str, Any]]) -> None:
    """Validate named image assets before rendering.

    Image paths in ``data/images.json`` are site-root paths such as
    ``/images/portrait.webp``. They must resolve beneath ``static/``.
    """
    errors: list[str] = []
    for key, asset in catalog.items():
        src = str(asset.get("src", "")).strip()
        if not src.startswith("/"):
            errors.append(f"images.{key}.src must start with '/': {src!r}")
            continue
        source_file = root / "static" / src.lstrip("/")
        if not source_file.exists():
            errors.append(f"images.{key} points to missing file: {source_file}")
        if "alt" not in asset:
            errors.append(f"images.{key} is missing an alt field")
    if errors:
        raise RuntimeError("Image catalog validation failed:\n- " + "\n- ".join(errors))


def resolve_image(catalog: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    """Return an image record by key, raising a useful error when absent."""
    try:
        return catalog[key]
    except KeyError as exc:
        raise KeyError(
            f"Unknown image key {key!r}. Add it to data/images.json first."
        ) from exc

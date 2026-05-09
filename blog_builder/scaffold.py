from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from .config import POSTS_DIR


def slugify_title(title: str) -> str:
    slug = unicodedata.normalize("NFKC", title).strip().lower()
    slug = slug.replace("_", "-").replace(" ", "-")
    slug = re.sub(r"[^\w\-]+", "-", slug, flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "post"


def create_post(title: str, *, now: datetime | None = None) -> Path:
    title = title.strip()
    if not title:
        raise ValueError("Post title cannot be empty.")

    created_at = now or datetime.now()
    path = POSTS_DIR / f"{slugify_title(title)}.md"
    if path.exists():
        raise FileExistsError(f"Post already exists: {path}")

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
title: {title}
date: {created_at.strftime("%Y-%m-%d %H:%M:%S")}
tags:
---

""",
        encoding="utf-8",
        newline="\n",
    )
    return path

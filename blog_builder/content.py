from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from .config import POSTS_DIR
from .markdown_renderer import extract_summary, markdown_to_html
from .models import Post


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("Markdown post must start with frontmatter delimited by ---")

    _, remainder = text.split("---\n", 1)
    if remainder.endswith("\n---"):
        frontmatter_text = remainder[:-4]
        body = ""
    else:
        try:
            frontmatter_text, body = remainder.split("\n---\n", 1)
        except ValueError as exc:
            raise ValueError("Frontmatter must end with a closing --- line") from exc

    metadata: dict[str, str] = {}
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid frontmatter line: {raw_line}")
        metadata[key.strip()] = value.strip()

    return metadata, body.lstrip()


def parse_tags(value: str) -> list[str]:
    if not value:
        return []
    parts = [item.strip() for item in value.split(",")]
    return [item for item in parts if item]


def slugify(path: Path) -> str:
    stem = unicodedata.normalize("NFKC", path.stem).strip().lower()
    stem = stem.replace("_", "-").replace(" ", "-")
    stem = re.sub(r"[^\w\-]+", "-", stem, flags=re.UNICODE)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return stem or "post"


def parse_date(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def resolve_updated_date(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def parse_sticky(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return 1 if value.lower() in {"true", "yes", "on"} else 0


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("published", "").lower() == "false":
            continue
        slug = metadata.get("slug", "").strip() or slugify(path)
        title = metadata["title"]
        date = parse_date(metadata["date"])
        updated = resolve_updated_date(path)
        sticky = parse_sticky(metadata.get("sticky", ""))
        summary = metadata.get("summary", "").strip() or extract_summary(body)
        read_time = metadata.get("read_time", "5 min")
        author = metadata.get("author", "Wens")
        tags = parse_tags(metadata.get("tags", ""))
        posts.append(
            Post(
                source_path=path,
                slug=slug,
                title=title,
                date=date,
                updated=updated,
                sticky=sticky,
                summary=summary,
                read_time=read_time,
                author=author,
                tags=tags,
                body_html=markdown_to_html(body),
            )
        )

    return sorted(posts, key=lambda post: (post.sticky, post.date), reverse=True)

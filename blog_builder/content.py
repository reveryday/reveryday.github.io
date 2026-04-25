from __future__ import annotations

import re
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

from .config import POSTS_DIR, ROOT
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


def resolve_updated_date(path: Path, metadata: dict[str, str], date: datetime) -> datetime:
    updated_value = metadata.get("updated", "").strip()
    if updated_value:
        return parse_date(updated_value)

    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={ROOT}",
                "log",
                "-1",
                "--format=%cI",
                "--",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return date

    git_updated = result.stdout.strip()
    if not git_updated:
        return date

    return datetime.fromisoformat(git_updated.replace("Z", "+00:00")).replace(tzinfo=None)


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("published", "").lower() == "false":
            continue
        slug = metadata.get("slug", "").strip() or slugify(path)
        title = metadata["title"]
        date = parse_date(metadata["date"])
        updated = resolve_updated_date(path, metadata, date)
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
                summary=summary,
                read_time=read_time,
                author=author,
                tags=tags,
                body_html=markdown_to_html(body),
            )
        )

    return sorted(posts, key=lambda post: post.date, reverse=True)

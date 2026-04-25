from __future__ import annotations

import shutil
from pathlib import Path

from .config import OUTPUT_DIR, ROOT
from .content import load_posts
from .templates import (
    render_archive,
    render_faq_page,
    render_friends_page,
    render_home,
    render_post_page,
    render_search_index,
    render_search_page,
    render_tags,
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def copy_static_assets(source_dir: Path, target_dir: Path) -> None:
    for source_path in source_dir.rglob("*"):
        if source_path.is_dir():
            continue
        relative = source_path.relative_to(source_dir)
        destination = target_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)


def main() -> None:
    posts = load_posts()
    if not posts:
        raise SystemExit("No Markdown posts found in posts/")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_static_assets(ROOT / "assets", OUTPUT_DIR / "assets")

    write_text(OUTPUT_DIR / "index.html", render_home(posts))
    write_text(OUTPUT_DIR / "archive.html", render_archive(posts))
    write_text(OUTPUT_DIR / "tags.html", render_tags(posts))
    write_text(OUTPUT_DIR / "search.html", render_search_page())
    write_text(OUTPUT_DIR / "faq.html", render_faq_page())
    write_text(OUTPUT_DIR / "friends.html", render_friends_page())
    write_text(OUTPUT_DIR / "assets" / "search.js", render_search_index(posts))

    for post in posts:
        write_text(OUTPUT_DIR / "posts" / f"{post.slug}.html", render_post_page(post))

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
    render_playground_page,
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


def remove_path(path: Path) -> None:
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except FileNotFoundError:
        return
    except PermissionError:
        print(f"Warning: could not remove stale build artifact: {path}")


def prune_empty_directories(root: Path) -> None:
    if not root.exists():
        return
    directories = sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in directories:
        try:
            path.rmdir()
        except OSError:
            continue


def prune_stale_posts(posts_dir: Path, current_slugs: set[str]) -> None:
    if not posts_dir.exists():
        return
    for path in posts_dir.glob("*.html"):
        if path.stem not in current_slugs:
            remove_path(path)


def prune_stale_assets(source_dir: Path, target_dir: Path) -> None:
    if not target_dir.exists():
        return
    expected_files = {
        path.relative_to(source_dir)
        for path in source_dir.rglob("*")
        if path.is_file()
    }
    expected_files.add(Path("search.js"))

    for path in sorted(
        (path for path in target_dir.rglob("*") if path.is_file()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if path.relative_to(target_dir) not in expected_files:
            remove_path(path)

    prune_empty_directories(target_dir)


def main() -> None:
    posts = load_posts()
    if not posts:
        raise SystemExit("No Markdown posts found in posts/")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prune_stale_posts(OUTPUT_DIR / "posts", {post.slug for post in posts})
    prune_stale_assets(ROOT / "assets", OUTPUT_DIR / "assets")
    copy_static_assets(ROOT / "assets", OUTPUT_DIR / "assets")

    write_text(OUTPUT_DIR / "index.html", render_home(posts))
    write_text(OUTPUT_DIR / "archive.html", render_archive(posts))
    write_text(OUTPUT_DIR / "tags.html", render_tags(posts))
    write_text(OUTPUT_DIR / "search.html", render_search_page())
    write_text(OUTPUT_DIR / "playground.html", render_playground_page())
    write_text(OUTPUT_DIR / "faq.html", render_faq_page())
    write_text(OUTPUT_DIR / "friends.html", render_friends_page())
    write_text(OUTPUT_DIR / "assets" / "search.js", render_search_index(posts))

    for post in posts:
        write_text(OUTPUT_DIR / "posts" / f"{post.slug}.html", render_post_page(post))

import json
import os
import sys

from blog_builder.builder import main
from blog_builder.config import POSTS_DIR
from blog_builder.content import MTIMES_FILE
from blog_builder.scaffold import create_post


def _write_mtime_manifest() -> None:
    if os.environ.get("CI", "").lower() == "true":
        return
    manifest = {
        path.name: path.stat().st_mtime
        for path in sorted(POSTS_DIR.glob("*.md"))
    }
    MTIMES_FILE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _print_usage() -> None:
    print('Usage: python build.py [n|new "Post Title"]')


def _run_cli(argv: list[str]) -> None:
    if not argv:
        _write_mtime_manifest()
        main()
        return

    command = argv[0].lower()
    if command in {"n", "new"}:
        if len(argv) < 2:
            raise SystemExit('Missing post title. Usage: python build.py n "Post Title"')
        try:
            path = create_post(" ".join(argv[1:]))
        except (FileExistsError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Created post: {path}")
        return

    _print_usage()
    raise SystemExit(f"Unknown command: {argv[0]}")


if __name__ == "__main__":
    _run_cli(sys.argv[1:])

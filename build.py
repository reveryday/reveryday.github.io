import json
import os

from blog_builder.builder import main
from blog_builder.config import POSTS_DIR
from blog_builder.content import MTIMES_FILE


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


if __name__ == "__main__":
    _write_mtime_manifest()
    main()

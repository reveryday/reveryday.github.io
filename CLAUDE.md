# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A dependency-free static blog generator written in Python (stdlib only). Markdown posts in `posts/` are compiled to a static site in `dist/`, which is deployed to GitHub Pages. The Markdown parser, templating, and feed/sitemap generation are all hand-rolled — there are no third-party packages and no `requirements.txt`.

## Commands

```bash
python build.py                  # Build the whole site into dist/
python build.py n "Post Title"   # Scaffold a new post in posts/ (also: `new`)
```

There is no test suite, linter, or package manifest. "Running" the site is just opening `dist/index.html` after a build, or relying on the GitHub Actions deploy.

## Build pipeline

`build.py` is a thin CLI wrapper around `blog_builder`. Flow:

1. **`build.py`** — dispatches `n`/`new` to `scaffold.create_post`, otherwise runs the full build. Before building locally it writes `posts/.mtimes.json` (see "Updated dates" below). Skipped when `CI=true`.
2. **`content.load_posts`** — globs `posts/*.md`, parses each, returns `Post` objects sorted by `(sticky, date)` descending. Posts with `published: false` are dropped.
3. **`builder.main`** — the orchestrator. Prunes stale output, copies `assets/` → `dist/assets/`, then renders every page via `templates.*` and writes it. Adding a new output page means adding a `render_*` function in `templates.py` and a `write_text(...)` call in `builder.main`.

Module responsibilities in `blog_builder/`:

- `config.py` — **all site-wide settings live here**: title, base URL, nav links, social links, CDN `<link>`/`<script>` tags (KaTeX, highlight.js) injected via `HEAD_EXTRAS`/`FOOTER_SCRIPTS`. Change site metadata or nav here, not in templates.
- `models.py` — the `Post` dataclass and its display/URL properties.
- `content.py` — frontmatter parsing, slugify, date/tag/sticky parsing, mtime manifest.
- `markdown_renderer.py` — the custom Markdown→HTML converter (see below).
- `templates.py` — every page is a Python f-string. Produces HTML pages plus `sitemap.xml`, `robots.txt`, `feed.xml`, and the `search.js` index.
- `scaffold.py` — `python build.py new` post creation.

## Things that are easy to get wrong

- **The Markdown renderer is bespoke and line-based** (`markdown_renderer.py`). It supports a deliberately limited subset: headings, paragraphs, `-`/`N.` lists (with nested-list recursion), blockquotes, fenced code, `$...$` inline + `$$...$$` block math, Markdown images with `{ width=50% }` attributes, and raw `<img>`/`<p>` passthrough. It is **not** CommonMark — no tables, no setext headings, no reference links, single-line blockquotes only. When a post renders wrong, the fix is usually here, and edits risk regressions across all posts. Inline rendering stashes code/math/raw-HTML as `@@TOKEN@@` placeholders before escaping, then restores them — preserve that order when editing `render_inline`.

- **Updated dates depend on `posts/.mtimes.json`.** `date` (frontmatter) is the publish date; "Updated" is derived from file mtime. Because git does not preserve mtimes on checkout, `build.py` snapshots local mtimes into `posts/.mtimes.json` (committed) so CI shows stable updated dates. When `CI=true` the manifest is **not** rewritten, and `resolve_updated_date` reads it. Don't delete this file or updated dates will jump to checkout time on the next CI build.

- **Math and syntax highlighting are client-side via CDN.** The renderer only emits `\(...\)`, `\[...\]`, and `<pre><code class="language-x">`. KaTeX auto-render and highlight.js (loaded in `config.FOOTER_SCRIPTS`) do the actual work in the browser. Fortran is the only extra highlight.js language explicitly loaded.

- **`dist/` is generated and gitignored** — never hand-edit files there; they are overwritten every build. The build prunes stale `dist/posts/*.html` and stale `dist/assets/*` so removing a post or asset cleans up correctly.

- **Slugs** come from `slug:` frontmatter if present, else a slugify of the filename (Unicode-aware, so CJK filenames are kept). Changing a filename or slug changes the post URL.

## Frontmatter fields

`title` and `date` are required. Optional: `summary` (else auto-extracted from first text line), `tags` (comma-separated), `sticky` (int pin weight), `slug`, `published` (`false` to exclude).

## Deployment

`.github/workflows/deploy.yml` runs `python build.py` on push to `main` (with `CI=true`) and publishes `dist/` to GitHub Pages. Python `3.x`, no install step. The remote default branch is `main`.

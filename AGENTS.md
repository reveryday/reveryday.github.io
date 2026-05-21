# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python static blog generator. Source code lives in `blog_builder/`: `builder.py` coordinates site generation, `content.py` loads Markdown posts, `markdown_renderer.py` renders Markdown, `templates.py` owns HTML templates, and `config.py` stores site settings. Blog posts live in `posts/*.md` with front matter. Shared CSS and browser scripts live in `assets/`. Generated output is written to `dist/` and deployed by `.github/workflows/deploy.yml`.

## Build, Test, and Development Commands

- `python build.py`: build the full static site into `dist/`.
- `python build.py n "Post Title"` or `python build.py new "Post Title"`: scaffold a new Markdown post in `posts/`.
- Open `dist/index.html` in a browser to preview the generated site locally.

There is no separate dev server or package manager workflow for the core site.

## Coding Style & Naming Conventions

Use Python 3 style with 4-space indentation, type hints where they improve clarity, and small functions that match the current module boundaries. Keep generated HTML template strings readable and escape user-facing content with `html.escape` where appropriate. Use snake_case for Python functions and variables. Markdown post filenames may be English or Chinese; prefer stable slugs in front matter when URLs should not change.

## Testing Guidelines

No formal test suite is currently present. Validate changes by running `python build.py` and checking relevant files in `dist/`. For template, CSS, or Markdown-rendering changes, manually inspect `dist/index.html`, one generated post under `dist/posts/`, and any affected index page such as `archive.html`, `tags.html`, or `search.html`.

## Commit & Pull Request Guidelines

Recent commit messages are very short, so keep commits concise but descriptive, for example `update blog colors` or `fix markdown image sizing`. Pull requests should describe the user-visible change, list build verification (`python build.py`), and include screenshots when changing UI, layout, or generated pages.

## Generated Files & Configuration Notes

`dist/` is generated output; edit source files in `blog_builder/`, `assets/`, or `posts/` first, then rebuild. Running `python build.py` locally updates `posts/.mtimes.json`; avoid committing that file when it only contains timestamp churn. In CI, the mtime manifest is skipped via the `CI=true` environment variable.

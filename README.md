# MyBlog

A reading-first static blog.

## Local preview

1. Write or edit Markdown posts in `posts/`.
2. Run `python build.py`.
3. Open `index.html` directly in a browser.

## Publish to GitHub Pages

1. Push this repository to the `main` branch.
2. In GitHub, open `Settings -> Pages`.
3. Set the source to `GitHub Actions`.
4. Every push to `main` will run `python build.py` and deploy the generated site.

## Add a new post

Create a new `posts/*.md` file with frontmatter like this:

```md
---
title: My New Post
date: 2026-04-19
summary: One-sentence summary for the homepage and search page.
read_time: 5 min
author: Wens
tags: Writing, Notes
---

Your Markdown content starts here.
```

The build step will automatically generate:

- `posts/*.html`
- `index.html`
- `archive.html`
- `tags.html`
- `assets/search.js`

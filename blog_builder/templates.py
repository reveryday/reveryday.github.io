from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from urllib.parse import quote

from .config import (
    FOOTER_SCRIPTS,
    HEAD_EXTRAS,
    HOME_EYEBROW,
    HOME_HEADING,
    HOME_LEDE,
    NAV_LINKS,
    SITE_AUTHOR,
    SITE_BASE_URL,
    SITE_DESCRIPTION,
    SITE_TITLE,
    SOCIAL_LINKS,
)
from .models import Post


def _absolute_url(path: str) -> str:
    base = SITE_BASE_URL if SITE_BASE_URL.endswith("/") else SITE_BASE_URL + "/"
    return base + quote(path, safe="/")


def _iso_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def render_nav(current_href: str) -> str:
    links: list[str] = []
    for label, href in NAV_LINKS:
        current = ' aria-current="page"' if href == current_href else ""
        links.append(f'            <a href="{href}"{current}>{label}</a>')
    return "\n".join(links)


def render_post_nav() -> str:
    return "\n".join(f'            <a href="../{href}">{label}</a>' for label, href in NAV_LINKS)


def render_layout(title: str, content: str, description: str = "", *, page_url: str = "") -> str:
    meta_description = description or SITE_DESCRIPTION
    full_url = _absolute_url(page_url)
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(meta_description)}" />
    <link rel="canonical" href="{escape(full_url)}" />
    <meta property="og:title" content="{escape(title)}" />
    <meta property="og:description" content="{escape(meta_description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{escape(full_url)}" />
    <meta property="og:site_name" content="{escape(SITE_TITLE)}" />
    <meta name="twitter:card" content="summary" />
    <link rel="alternate" type="application/atom+xml" href="feed.xml" title="{escape(SITE_TITLE)} feed" />
    <link rel="stylesheet" href="assets/style.css" />
{HEAD_EXTRAS}
  </head>
  <body>
    <div class="page-shell">
{content}
    </div>
{FOOTER_SCRIPTS}
  </body>
</html>
"""


def render_page_header(current_href: str, heading: str) -> str:
    return f"""      <header class="site-header compact">
        <nav class="top-nav" aria-label="Primary">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav(current_href)}
          </div>
        </nav>
        <h1>{heading}</h1>
      </header>"""


def render_home(posts: list[Post]) -> str:
    cards = []
    for post in posts:
        cards.append(
            f"""        <article class="post-card">
          <h2><a href="{post.url}">{escape(post.title)}</a></h2>
          <p>{escape(post.summary)}</p>
          <p class="meta">Date: {post.display_date} | Updated: {post.display_updated} | Tags: {escape(post.display_tags)}</p>
        </article>"""
        )

    socials = "\n".join(
        f'            <a href="{href}" target="_blank" rel="noreferrer">{escape(label)}</a>'
        for label, href in SOCIAL_LINKS
    )
    eyebrow_html = f'          <p class="eyebrow">{escape(HOME_EYEBROW)}</p>\n' if HOME_EYEBROW else ""

    content = f"""      <header class="site-header">
        <nav class="top-nav" aria-label="Primary">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav("index.html")}
          </div>
        </nav>
        <section class="hero">
{eyebrow_html}\
          <h1>{HOME_HEADING}</h1>
          <p class="lede">
            {HOME_LEDE}
          </p>
          <div class="social-links">
{socials}
          </div>
        </section>
      </header>

      <main class="post-feed">
{chr(10).join(cards)}
      </main>"""

    return render_layout(SITE_TITLE, content, SITE_DESCRIPTION, page_url="")


def render_archive(posts: list[Post]) -> str:
    items = "\n".join(
        f'          <li><span>{post.iso_date}</span> <a href="{post.url}">{escape(post.title)}</a></li>'
        for post in posts
    )
    content = f"""{render_page_header("archive.html", "Archive")}

      <main class="content-page">
        <ul class="archive-list">
{items}
        </ul>
      </main>"""
    return render_layout(f"Archive | {SITE_TITLE}", content, page_url="archive.html")


def render_tags(posts: list[Post]) -> str:
    grouped: defaultdict[str, list[Post]] = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            grouped[tag].append(post)

    sections = []
    for tag in sorted(grouped):
        links = "\n".join(
            f'          <p><a href="{post.url}">{escape(post.title)}</a></p>' for post in grouped[tag]
        )
        sections.append(
            f"""        <section class="tag-group">
          <h2>{escape(tag)}</h2>
{links}
        </section>"""
        )

    empty_state = '<p class="meta">No tags yet.</p>' if not sections else ""
    body = "\n".join(sections) if sections else f"        {empty_state}"
    content = f"""{render_page_header("tags.html", "Tags")}

      <main class="content-page">
{body}
      </main>"""
    return render_layout(f"Tags | {SITE_TITLE}", content, page_url="tags.html")


def render_search_page() -> str:
    content = f"""{render_page_header("search.html", "Search")}

      <main class="content-page">
        <label class="search-panel" for="query">
          <span class="search-label">Search by title or summary</span>
          <input id="query" type="search" placeholder="Try 'deployment' or 'reading'" />
        </label>
        <div id="results" class="search-results"></div>
      </main>
      <script src="assets/search.js"></script>"""
    return render_layout(f"Search | {SITE_TITLE}", content, page_url="search.html")


def render_playground_page() -> str:
    content = f"""{render_page_header("playground.html", "Playground")}

      <main class="content-page playground-page">
        <p class="meta">Write code and run it in your browser. Powered by the free, public <a href="https://godbolt.org/" target="_blank" rel="noreferrer">Compiler Explorer</a> API. Your code, language, and stdin are saved locally.</p>

        <div class="pg-lang-buttons" role="group" aria-label="Language">
          <button type="button" class="pg-lang-btn" data-lang="python" aria-pressed="false">Python</button>
          <button type="button" class="pg-lang-btn" data-lang="cpp" aria-pressed="false">C++</button>
          <button type="button" class="pg-lang-btn" data-lang="fortran" aria-pressed="false">Fortran</button>
        </div>

        <div class="pg-editor-wrap">
          <textarea id="pg-code" spellcheck="false"></textarea>
        </div>

        <div class="pg-section-label">Stdin (optional)</div>
        <textarea id="pg-stdin" class="pg-stdin" spellcheck="false" placeholder="Input passed to the program's standard input..."></textarea>

        <div class="pg-run-row">
          <button type="button" id="pg-run" class="pg-run-btn">&#9654; Run</button>
          <span id="pg-compiler-info" class="pg-compiler-info"></span>
        </div>

        <div class="pg-output-header">
          <span class="pg-section-label">Output</span>
          <button type="button" id="pg-clear" class="pg-clear-btn">Clear</button>
        </div>
        <div id="pg-output" class="pg-output"></div>
      </main>

      <link rel="stylesheet" href="assets/playground.css" />
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/codemirror@5.65.16/lib/codemirror.min.css" />
      <script defer src="https://cdn.jsdelivr.net/npm/codemirror@5.65.16/lib/codemirror.min.js"></script>
      <script defer src="https://cdn.jsdelivr.net/npm/codemirror@5.65.16/mode/python/python.min.js"></script>
      <script defer src="https://cdn.jsdelivr.net/npm/codemirror@5.65.16/mode/clike/clike.min.js"></script>
      <script defer src="https://cdn.jsdelivr.net/npm/codemirror@5.65.16/mode/fortran/fortran.min.js"></script>
      <script defer src="assets/playground.js"></script>"""
    return render_layout(f"Playground | {SITE_TITLE}", content, page_url="playground.html")


def render_faq_page() -> str:
    content = f"""{render_page_header("faq.html", "FAQ")}

      <main class="content-page prose">
        <h2>What is this blog for?</h2>
        <p>Long-form notes, technical essays, and project writeups.</p>
        <h2>How is it deployed?</h2>
        <p>As a static site on GitHub Pages through a GitHub Actions workflow.</p>
      </main>"""
    return render_layout(f"FAQ | {SITE_TITLE}", content, page_url="faq.html")


def render_friends_page() -> str:
    content = f"""{render_page_header("friends.html", "Friends")}

      <main class="content-page prose">
        <h2>Friend Links</h2>
        <p>
          <a href="https://r0otsu.github.io/" target="_blank" rel="noreferrer">
            r0otsu.github.io
          </a>
        </p>
      </main>"""
    return render_layout(f"Friends | {SITE_TITLE}", content, page_url="friends.html")


def render_search_index(posts: list[Post]) -> str:
    search_posts = [
        {
            "title": post.title,
            "summary": post.summary,
            "url": post.url,
        }
        for post in posts
    ]
    return "const posts = " + json.dumps(search_posts, ensure_ascii=False, indent=2) + ";\n\n" + SEARCH_SCRIPT_BODY


SEARCH_SCRIPT_BODY = """const queryInput = document.querySelector("#query");
const results = document.querySelector("#results");

function render(matches) {
  if (!results) {
    return;
  }

  if (matches.length === 0) {
    results.innerHTML = '<p class="meta">No matching posts yet.</p>';
    return;
  }

  results.innerHTML = matches
    .map(
      (post) => `
        <article class="search-result">
          <h2><a href="${post.url}">${post.title}</a></h2>
          <p>${post.summary}</p>
        </article>
      `
    )
    .join("");
}

if (queryInput) {
  render(posts);

  queryInput.addEventListener("input", (event) => {
    const term = event.target.value.trim().toLowerCase();
    const matches = posts.filter((post) => {
      return (
        post.title.toLowerCase().includes(term) ||
        post.summary.toLowerCase().includes(term)
      );
    });

    render(matches);
  });
}
"""


def render_post_page(post: Post) -> str:
    canonical = _absolute_url(post.url)
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(post.title)} | {SITE_TITLE}</title>
    <meta name="description" content="{escape(post.summary)}" />
    <link rel="canonical" href="{escape(canonical)}" />
    <meta property="og:title" content="{escape(post.title)}" />
    <meta property="og:description" content="{escape(post.summary)}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{escape(canonical)}" />
    <meta property="og:site_name" content="{escape(SITE_TITLE)}" />
    <meta property="article:published_time" content="{_iso_datetime(post.date)}" />
    <meta property="article:modified_time" content="{_iso_datetime(post.updated)}" />
    <meta name="twitter:card" content="summary" />
    <link rel="alternate" type="application/atom+xml" href="../feed.xml" title="{escape(SITE_TITLE)} feed" />
    <link rel="stylesheet" href="../assets/style.css" />
    {HEAD_EXTRAS}
  </head>
  <body>
    <div class="page-shell">
      <header class="site-header compact">
        <nav class="top-nav" aria-label="Primary">
          <a class="brand" href="../index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_post_nav()}
          </div>
        </nav>
      </header>

      <main class="article-page prose">
        <article>
          <h1>{escape(post.title)}</h1>
          <p class="meta">Date: {post.display_date} | Updated: {post.display_updated} | Tags: {escape(post.display_tags)}</p>
          {post.body_html}
        </article>
      </main>
    </div>
    {FOOTER_SCRIPTS}
  </body>
</html>
"""


_STATIC_SITEMAP_PAGES = [
    ("", "weekly"),
    ("archive.html", "weekly"),
    ("tags.html", "monthly"),
    ("search.html", "monthly"),
    ("playground.html", "monthly"),
    ("faq.html", "yearly"),
    ("friends.html", "yearly"),
]


def render_sitemap(posts: list[Post]) -> str:
    entries: list[str] = []
    for path, freq in _STATIC_SITEMAP_PAGES:
        entries.append(
            f"  <url>\n    <loc>{escape(_absolute_url(path))}</loc>\n"
            f"    <changefreq>{freq}</changefreq>\n  </url>"
        )
    for post in posts:
        entries.append(
            f"  <url>\n    <loc>{escape(_absolute_url(post.url))}</loc>\n"
            f"    <lastmod>{post.updated.strftime('%Y-%m-%d')}</lastmod>\n  </url>"
        )
    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def render_robots_txt() -> str:
    sitemap_url = _absolute_url("sitemap.xml")
    return (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {sitemap_url}\n"
    )


def render_feed_atom(posts: list[Post], limit: int = 20) -> str:
    latest = posts[:limit]
    if latest:
        feed_updated = _iso_datetime(max(post.updated for post in latest))
    else:
        feed_updated = _iso_datetime(datetime.now(timezone.utc).replace(tzinfo=None))

    entries: list[str] = []
    for post in latest:
        entry_url = _absolute_url(post.url)
        entries.append(
            "  <entry>\n"
            f"    <title>{escape(post.title)}</title>\n"
            f'    <link href="{escape(entry_url)}" />\n'
            f"    <id>{escape(entry_url)}</id>\n"
            f"    <published>{_iso_datetime(post.date)}</published>\n"
            f"    <updated>{_iso_datetime(post.updated)}</updated>\n"
            f"    <summary>{escape(post.summary)}</summary>\n"
            "  </entry>"
        )

    site_url = _absolute_url("")
    feed_url = _absolute_url("feed.xml")
    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"  <title>{escape(SITE_TITLE)}</title>\n"
        f"  <subtitle>{escape(SITE_DESCRIPTION)}</subtitle>\n"
        f'  <link href="{escape(site_url)}" />\n'
        f'  <link href="{escape(feed_url)}" rel="self" />\n'
        f"  <id>{escape(site_url)}</id>\n"
        f"  <updated>{feed_updated}</updated>\n"
        f"  <author><name>{escape(SITE_AUTHOR)}</name></author>\n"
        f"{body}\n"
        "</feed>\n"
    )

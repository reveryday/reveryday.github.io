from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from html import escape, unescape
from urllib.parse import quote

from .config import (
    FOOTER_SCRIPTS,
    HEAD_EXTRAS,
    HOME_HEADING,
    NAV_LINKS,
    PAGES_DIR,
    SITE_AUTHOR,
    SITE_BASE_URL,
    SITE_DESCRIPTION,
    SITE_TITLE,
)
from .markdown_renderer import markdown_to_html
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
<html lang="zh-CN">
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


def render_page_header(current_href: str, heading: str = "") -> str:
    heading_html = f"\n        <h1>{heading}</h1>" if heading else ""
    return f"""      <header class="site-header compact">
        <nav class="top-nav" aria-label="主导航">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav(current_href)}
          </div>
        </nav>{heading_html}
      </header>"""


def _tag_color_class(tag: str) -> str:
    return f"tag-color-{sum(ord(char) for char in tag) % 5}"


def render_home(posts: list[Post]) -> str:
    cards = []
    for post in posts:
        tags = "".join(
            f'            <span class="tag-chip {_tag_color_class(tag)}">{escape(tag)}</span>\n'
            for tag in post.tags
        )
        tags_html = tags if tags else '            <span class="tag-chip muted">无</span>\n'
        cards.append(
            f"""        <article class="post-card">
          <h2><a href="{post.url}">{escape(post.title)}</a></h2>
          <p class="post-summary">{escape(post.summary)}</p>
          <div class="post-meta-row">
            <span>发布于 {post.display_date}</span>
            <span>更新于 {post.display_updated}</span>
          </div>
          <div class="post-tags" aria-label="标签">
{tags_html.rstrip()}
          </div>
        </article>"""
        )

    content = f"""      <header class="site-header">
        <nav class="top-nav" aria-label="主导航">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav("index.html")}
          </div>
        </nav>
      </header>

      <p class="home-motto">{escape(HOME_HEADING)}</p>

      <main class="post-feed">
{chr(10).join(cards)}
      </main>"""

    return render_layout(SITE_TITLE, content, SITE_DESCRIPTION, page_url="")


def render_archive(posts: list[Post]) -> str:
    items = "\n".join(
        f'          <li><span>{post.iso_date}</span> <a href="{post.url}">{escape(post.title)}</a></li>'
        for post in posts
    )
    content = f"""{render_page_header("archive.html")}

      <main class="content-page">
        <ul class="archive-list">
{items}
        </ul>
      </main>"""
    return render_layout(f"归档 | {SITE_TITLE}", content, page_url="archive.html")


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

    empty_state = '<p class="meta">暂无标签。</p>' if not sections else ""
    body = "\n".join(sections) if sections else f"        {empty_state}"
    content = f"""{render_page_header("tags.html")}

      <main class="content-page">
{body}
      </main>"""
    return render_layout(f"标签 | {SITE_TITLE}", content, page_url="tags.html")


def render_search_page() -> str:
    content = f"""{render_page_header("search.html")}

      <main class="content-page">
        <label class="search-panel" for="query">
          <input id="query" type="search" placeholder="搜索文章标题、摘要或正文" />
        </label>
        <div id="results" class="search-results"></div>
      </main>
      <script src="assets/search.js"></script>"""
    return render_layout(f"搜索 | {SITE_TITLE}", content, page_url="search.html")


def render_playground_page() -> str:
    content = f"""      <header class="site-header compact">
        <nav class="top-nav" aria-label="主导航">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav("playground.html")}
          </div>
        </nav>
      </header>

      <main class="content-page playground-page">
        <div class="pg-lang-buttons" role="group" aria-label="Language">
          <button type="button" class="pg-lang-btn" data-lang="python" aria-pressed="false">Python</button>
          <button type="button" class="pg-lang-btn" data-lang="cpp" aria-pressed="false">C++</button>
          <button type="button" class="pg-lang-btn" data-lang="fortran" aria-pressed="false">Fortran</button>
        </div>

        <div class="pg-editor-wrap">
          <textarea id="pg-code" spellcheck="false"></textarea>
        </div>

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


def render_collection_page() -> str:
    source = (PAGES_DIR / "collection.md").read_text(encoding="utf-8")
    content = f"""{render_page_header("collection.html")}

      <main class="content-page prose collection-page">
          {markdown_to_html(source)}
      </main>"""
    return render_layout(f"收藏 | {SITE_TITLE}", content, page_url="collection.html")


def render_friends_page() -> str:
    content = f"""{render_page_header("friends.html")}

      <main class="content-page friends-page">
        <section class="friends-intro">
          <h2>值得一读</h2>
        </section>

        <div class="friend-grid">
          <a class="friend-card" href="https://r0otsu.github.io/" target="_blank" rel="noreferrer">
            <span class="friend-mark" aria-hidden="true">R</span>
            <span class="friend-body">
              <span class="friend-name">r0otsu</span>
              <span class="friend-note">放一些无聊的东西.</span>
            </span>
            <span class="friend-arrow" aria-hidden="true">-&gt;</span>
          </a>
        </div>
      </main>"""
    return render_layout(f"友链 | {SITE_TITLE}", content, page_url="friends.html")


def render_tracker_page() -> str:
    content = f"""{render_page_header("tracker.html", "Work Hours Tracker")}

      <main class="content-page tracker-page">
        <section class="tracker-summary" aria-label="Tracker summary">
          <div>
            <span class="tracker-label">Work target</span>
            <strong id="work-target">-- h/day</strong>
          </div>
          <div>
            <span class="tracker-label">Completion</span>
            <strong id="work-completion">--</strong>
          </div>
          <div>
            <span class="tracker-label">Total hours</span>
            <strong id="total-hours">-- h</strong>
          </div>
        </section>

        <section class="tracker-section" aria-labelledby="work-calendar-title">
          <div class="tracker-section-header">
            <h2 id="work-calendar-title">Work check-in</h2>
            <p class="meta">Daily target completion over the latest year.</p>
          </div>
          <div class="calendar-wrap" aria-label="Work target calendar">
            <div id="work-calendar" class="work-calendar"></div>
          </div>
          <div class="calendar-legend" aria-label="Calendar legend">
            <span>No record</span>
            <span class="calendar-swatch empty"></span>
            <span class="calendar-swatch partial"></span>
            <span class="calendar-swatch done"></span>
            <span>Done</span>
          </div>
        </section>

        <section class="tracker-section" aria-labelledby="work-chart-title">
          <div class="tracker-section-header">
            <div>
              <h2 id="work-chart-title">Work hours</h2>
              <p class="meta">Switch between daily, weekly, and monthly views.</p>
            </div>
            <div class="chart-tabs" role="group" aria-label="Work hours chart view">
              <button type="button" data-view="day" aria-pressed="true">Day</button>
              <button type="button" data-view="week" aria-pressed="false">Week</button>
              <button type="button" data-view="month" aria-pressed="false">Month</button>
            </div>
          </div>
          <div id="work-chart" class="study-chart" aria-label="Work hours line chart"></div>
        </section>
      </main>

      <script src="assets/tracker-data.js"></script>
      <script src="assets/tracker.js"></script>"""
    return render_layout(f"Work Hours Tracker | {SITE_TITLE}", content, page_url="tracker.html")


def _search_text(body_html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def render_search_index(posts: list[Post]) -> str:
    search_posts = [
        {
            "title": post.title,
            "summary": post.summary,
            "url": post.url,
            "content": _search_text(post.body_html),
        }
        for post in posts
    ]
    return "const posts = " + json.dumps(search_posts, ensure_ascii=False, indent=2) + ";\n\n" + SEARCH_SCRIPT_BODY


def render_article_toc(post: Post) -> str:
    counters: list[int] = []
    numbered_links: list[tuple[str, str, str]] = []
    for item in post.toc:
        level = max(1, min(item.level, 4))
        while len(counters) < level:
            counters.append(0)
        counters = counters[:level]
        counters[-1] += 1
        number = ".".join(str(value) for value in counters if value)
        numbered_links.append((f"toc-level-{level}", number, item.title))

    links = "\n".join(
        f'            <a class="{class_name}" href="#{escape(item.anchor, quote=True)}">'
        f'<span class="toc-number">{number}</span><span>{escape(title)}</span></a>'
        for item, (class_name, number, title) in zip(post.toc, numbered_links)
    )
    return f"""        <aside class="article-toc" aria-label="文章目录">
          <p class="article-toc-title">目录</p>
          <nav>
{links}
          </nav>
        </aside>"""


SEARCH_SCRIPT_BODY = """const queryInput = document.querySelector("#query");
const results = document.querySelector("#results");

function render(matches) {
  if (!results) {
    return;
  }

  if (matches.length === 0) {
    results.innerHTML = '<p class="meta">没有找到匹配的文章。</p>';
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
        post.summary.toLowerCase().includes(term) ||
        (post.content && post.content.toLowerCase().includes(term))
      );
    });

    render(matches);
  });
}
"""


def render_post_page(post: Post) -> str:
    canonical = _absolute_url(post.url)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
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
      <main class="article-page prose has-toc">
{render_article_toc(post)}
        <article class="article-content">
          <h1>{escape(post.title)}</h1>
          <p class="meta article-meta">
            <span>发布于 {post.display_date}</span>
            <span>更新于 {post.display_updated}</span>
            <span>标签 {escape(post.display_tags)}</span>
          </p>
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
    ("tracker.html", "weekly"),
    ("faq.html", "yearly"),
    ("friends.html", "yearly"),
    ("collection.html", "weekly"),
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

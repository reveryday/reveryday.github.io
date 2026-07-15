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
from .markdown_renderer import markdown_to_html_with_toc
from .models import Post, TocItem


_ICONS = {
    "arrow-up": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6"/></svg>',
    "arrow-left": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>',
    "arrow-right": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
    "external-link": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5h5v5m0-5-8 8"/><path d="M18 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    "moon": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 15.2A8.5 8.5 0 0 1 8.8 4a8.5 8.5 0 1 0 11.2 11.2Z"/></svg>',
    "play": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 7 8 5-8 5Z"/></svg>',
    "search": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m15.5 15.5 4 4"/></svg>',
}


def _icon(name: str) -> str:
    return _ICONS[name]


def _brand(prefix: str = "") -> str:
    return (
        f'<a class="brand" href="{prefix}index.html">'
        f'<span class="brand-name">{escape(SITE_TITLE)}</span>'
        '<span class="brand-mark" aria-hidden="true">W<span>/</span></span></a>'
    )


def _absolute_url(path: str) -> str:
    base = SITE_BASE_URL if SITE_BASE_URL.endswith("/") else SITE_BASE_URL + "/"
    return base + quote(path, safe="/")


def _iso_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _tag_slug(tag: str) -> str:
    normalized = tag.strip().lower().replace(" ", "-")
    slug = re.sub(r"[^\w\-]+", "-", normalized, flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "tag"


def render_footer() -> str:
    year = datetime.now().year
    return f"""      <footer class="site-footer">
        <span>© {year} {escape(SITE_TITLE)}</span>
        <span class="footer-wish">做个有梦想有行动有毅力有棱角且成熟的人</span>
        <nav class="footer-links" aria-label="页脚">
          <a href="#top">回到顶部 {_icon("arrow-up")}</a>
        </nav>
      </footer>"""


def _render_nav(current_href: str, prefix: str = "") -> str:
    links: list[str] = []
    for label, href in NAV_LINKS:
        current = ' aria-current="page"' if href == current_href else ""
        links.append(f'            <a href="{prefix}{href}"{current}>{label}</a>')
    search_current = ' aria-current="page"' if current_href == "search.html" else ""
    links.append(
        f'            <a class="nav-icon" href="{prefix}search.html" aria-label="搜索" title="搜索"{search_current}>{_icon("search")}</a>'
    )
    links.append(
        f'            <button class="theme-toggle nav-icon" type="button" aria-label="切换深色模式" title="切换显示模式">{_icon("moon")}</button>'
    )
    return "\n".join(links)


def render_nav(current_href: str) -> str:
    return _render_nav(current_href)


def render_post_nav() -> str:
    return _render_nav("", "../")


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
    <div class="page-shell" id="top">
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
          {_brand()}
          <div class="nav-links">
{render_nav(current_href)}
          </div>
        </nav>{heading_html}
      </header>"""


def _tag_color_class(tag: str) -> str:
    return f"tag-color-{sum(ord(char) for char in tag) % 5}"


def render_home_post_nav(posts: list[Post], start: int = 1) -> str:
    links = "\n".join(
        f'            <a href="{post.url}"><span class="toc-number">{index}</span>'
        f"<span>{escape(post.title)}</span></a>"
        for index, post in enumerate(posts, start=start)
    )
    return f"""      <aside class="article-toc home-post-nav" aria-label="文章导航">
        <p class="article-toc-title">文章</p>
        <nav>
{links}
        </nav>
      </aside>"""


def _home_page_href(page: int) -> str:
    return "index.html" if page <= 1 else f"page{page}.html"


def render_home_pagination(page: int, total_pages: int) -> str:
    if total_pages <= 1:
        return ""

    if page > 1:
        prev_link = f'<a class="page-link page-prev" href="{_home_page_href(page - 1)}" rel="prev">{_icon("arrow-left")} 较新文章</a>'
    else:
        prev_link = '<span class="page-link page-prev is-empty" aria-hidden="true"></span>'

    if page < total_pages:
        next_link = f'<a class="page-link page-next" href="{_home_page_href(page + 1)}" rel="next">更早文章 {_icon("arrow-right")}</a>'
    else:
        next_link = '<span class="page-link page-next is-empty" aria-hidden="true"></span>'

    return f"""          <nav class="home-pagination" aria-label="分页">
            {prev_link}
            <span class="pagination-status" aria-current="page">{page} / {total_pages}</span>
            {next_link}
          </nav>"""


def render_home(posts: list[Post], *, page: int = 1, total_pages: int = 1, start_index: int = 1) -> str:
    cards = []
    for post in posts:
        tags = "".join(
            f'            <a class="tag-chip {_tag_color_class(tag)}" href="tags.html#{_tag_slug(tag)}">{escape(tag)}</a>\n'
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

    feed_counter = f' style="counter-reset: post {start_index - 1}"' if start_index > 1 else ""

    content = f"""      <header class="site-header">
        <nav class="top-nav" aria-label="主导航">
          {_brand()}
          <div class="nav-links">
{render_nav("index.html")}
          </div>
        </nav>
      </header>

      <div class="has-toc home-body">
{render_home_post_nav(posts, start=start_index)}
        <div class="home-main">
          <p class="home-motto">{escape(HOME_HEADING)}</p>

          <main class="post-feed"{feed_counter}>
{chr(10).join(cards)}
          </main>
{render_home_pagination(page, total_pages)}
        </div>
      </div>"""

    return render_layout(SITE_TITLE, content, SITE_DESCRIPTION, page_url=_home_page_href(page))


def render_archive(posts: list[Post]) -> str:
    grouped: defaultdict[int, list[Post]] = defaultdict(list)
    for post in posts:
        grouped[post.date.year].append(post)

    sections: list[str] = []
    for year in sorted(grouped, reverse=True):
        items = "\n".join(
            f'              <li><time datetime="{post.iso_date}">{post.date.strftime("%m.%d")}</time>'
            f'<a href="{post.url}">{escape(post.title)}</a></li>'
            for post in grouped[year]
        )
        sections.append(
            f"""        <section class="archive-year" aria-labelledby="archive-{year}">
          <h2 id="archive-{year}">{year}</h2>
          <ol class="archive-list">
{items}
          </ol>
        </section>"""
        )

    content = f"""{render_page_header("archive.html")}

      <main class="content-page archive-page">
{chr(10).join(sections)}
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
            f'          <li><a href="{post.url}">{escape(post.title)}</a></li>'
            for post in grouped[tag]
        )
        sections.append(
            f"""        <section class="tag-group" id="{_tag_slug(tag)}">
          <h2>{escape(tag)}</h2>
          <ol class="tag-post-list">
{links}
          </ol>
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
          {_brand()}
          <div class="nav-links">
{render_nav("playground.html")}
          </div>
        </nav>
      </header>

      <main class="content-page playground-page">
        <div class="pg-lang-buttons" role="group" aria-label="编程语言">
          <button type="button" class="pg-lang-btn" data-lang="python" aria-pressed="false">Python</button>
          <button type="button" class="pg-lang-btn" data-lang="cpp" aria-pressed="false">C++</button>
          <button type="button" class="pg-lang-btn" data-lang="fortran" aria-pressed="false">Fortran</button>
        </div>

        <div class="pg-editor-wrap">
          <textarea id="pg-code" spellcheck="false"></textarea>
        </div>

        <div class="pg-run-row">
          <button type="button" id="pg-run" class="pg-run-btn">{_icon("play")}<span>运行</span></button>
          <span id="pg-compiler-info" class="pg-compiler-info"></span>
        </div>

        <div class="pg-output-header">
          <span class="pg-section-label">输出</span>
          <button type="button" id="pg-clear" class="pg-clear-btn">清空</button>
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
    return render_layout(f"代码演练场 | {SITE_TITLE}", content, page_url="playground.html")


def render_faq_page() -> str:
    content = f"""{render_page_header("faq.html", "常见问题")}

      <main class="content-page prose">
        <h2>这个博客用来做什么？</h2>
        <p>记录长篇笔记、技术文章和项目总结。</p>
        <h2>博客如何部署？</h2>
        <p>通过 GitHub Actions 构建，并作为静态站点部署到 GitHub Pages。</p>
      </main>"""
    return render_layout(f"常见问题 | {SITE_TITLE}", content, page_url="faq.html")


def render_collection_page() -> str:
    source = (PAGES_DIR / "collection.md").read_text(encoding="utf-8")
    body_html, toc = markdown_to_html_with_toc(source)
    content = f"""{render_page_header("collection.html")}

      <main class="content-page prose collection-page has-toc">
{render_toc(toc)}
        <article class="collection-content">
          {body_html}
        </article>
      </main>"""
    return render_layout(f"收藏 | {SITE_TITLE}", content, page_url="collection.html")


def render_friends_page() -> str:
    content = f"""{render_page_header("friends.html")}

      <main class="content-page friends-page">
        <section class="friends-intro">
          <h2>值得一读</h2>
        </section>

        <div class="friend-grid">
          <a class="friend-card" href="https://wens-wu.github.io/index.html" target="_blank" rel="noreferrer">
            <span class="friend-mark" aria-hidden="true">W</span>
            <span class="friend-body">
              <span class="friend-name">Wens' Blog</span>
              <span class="friend-note">我的另一个博客</span>
            </span>
            <span class="friend-arrow">{_icon("external-link")}</span>
          </a>
          <a class="friend-card" href="https://r0otsu.github.io/" target="_blank" rel="noreferrer">
            <span class="friend-mark" aria-hidden="true">R</span>
            <span class="friend-body">
              <span class="friend-name">r0otsu</span>
              <span class="friend-note">放一些无聊的东西.</span>
            </span>
            <span class="friend-arrow">{_icon("external-link")}</span>
          </a>
        </div>
      </main>"""
    return render_layout(f"友链 | {SITE_TITLE}", content, page_url="friends.html")


def render_tracker_page() -> str:
    content = f"""{render_page_header("tracker.html", "工作记录")}

      <main class="content-page tracker-page">
        <section class="tracker-summary" aria-label="工作记录概览">
          <div>
            <span class="tracker-label">每日目标</span>
            <strong id="work-target">-- 小时/天</strong>
          </div>
          <div>
            <span class="tracker-label">完成情况</span>
            <strong id="work-completion">--</strong>
          </div>
          <div>
            <span class="tracker-label">累计时长</span>
            <strong id="total-hours">-- 小时</strong>
          </div>
        </section>

        <section class="tracker-section" aria-labelledby="work-calendar-title">
          <div class="tracker-section-header">
            <h2 id="work-calendar-title">工作打卡</h2>
            <p class="meta">最近一年的每日目标完成情况。</p>
          </div>
          <div class="calendar-wrap" aria-label="工作目标日历">
            <div id="work-calendar" class="work-calendar"></div>
          </div>
          <div class="calendar-legend" aria-label="日历图例">
            <span>无记录</span>
            <span class="calendar-swatch empty"></span>
            <span class="calendar-swatch partial"></span>
            <span class="calendar-swatch done"></span>
            <span>已完成</span>
          </div>
        </section>

        <section class="tracker-section" aria-labelledby="work-chart-title">
          <div class="tracker-section-header">
            <div>
              <h2 id="work-chart-title">工作时长</h2>
              <p class="meta">按日、周或月查看记录。</p>
            </div>
            <div class="chart-tabs" role="group" aria-label="工作时长图表视图">
              <button type="button" data-view="day" aria-pressed="true">日</button>
              <button type="button" data-view="week" aria-pressed="false">周</button>
              <button type="button" data-view="month" aria-pressed="false">月</button>
            </div>
          </div>
          <div id="work-chart" class="study-chart" aria-label="工作时长折线图"></div>
        </section>
      </main>

      <script src="assets/tracker-data.js"></script>
      <script src="assets/tracker.js"></script>"""
    return render_layout(f"工作记录 | {SITE_TITLE}", content, page_url="tracker.html")


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


def render_toc(toc: list[TocItem]) -> str:
    counters: list[int] = []
    numbered_links: list[tuple[str, str, str]] = []
    for item in toc:
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
        for item, (class_name, number, title) in zip(toc, numbered_links)
    )
    return f"""        <details class="article-toc" open aria-label="文章目录">
          <summary class="article-toc-title">目录</summary>
          <nav>
{links}
          </nav>
        </details>"""


def render_article_toc(post: Post) -> str:
    return render_toc(post.toc)


SEARCH_SCRIPT_BODY = """const queryInput = document.querySelector("#query");
const results = document.querySelector("#results");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function highlight(text, term) {
  if (!term) {
    return escapeHtml(text);
  }
  const lower = text.toLowerCase();
  let out = "";
  let from = 0;
  let at = lower.indexOf(term, from);
  while (at !== -1) {
    out += escapeHtml(text.slice(from, at));
    out += "<mark>" + escapeHtml(text.slice(at, at + term.length)) + "</mark>";
    from = at + term.length;
    at = lower.indexOf(term, from);
  }
  return out + escapeHtml(text.slice(from));
}

function snippet(content, term) {
  if (!content) {
    return "";
  }
  if (!term) {
    return content.slice(0, 150);
  }
  const at = content.toLowerCase().indexOf(term);
  if (at === -1) {
    return content.slice(0, 150);
  }
  const start = Math.max(0, at - 60);
  const end = Math.min(content.length, at + term.length + 110);
  return (start > 0 ? "…" : "") + content.slice(start, end) + (end < content.length ? "…" : "");
}

function render(matches, term) {
  if (!results) {
    return;
  }

  if (matches.length === 0) {
    results.innerHTML = '<p class="meta">没有找到匹配的文章。</p>';
    return;
  }

  results.innerHTML = matches
    .map((post) => {
      const body = term
        ? '<p class="search-snippet">' + highlight(snippet(post.content || post.summary, term), term) + "</p>"
        : "<p>" + escapeHtml(post.summary) + "</p>";
      return (
        '<article class="search-result">' +
        '<h2><a href="' + post.url + '">' + highlight(post.title, term) + "</a></h2>" +
        body +
        "</article>"
      );
    })
    .join("");
}

if (queryInput) {
  render(posts, "");

  queryInput.addEventListener("input", (event) => {
    const term = event.target.value.trim().toLowerCase();
    const matches = posts.filter((post) => {
      return (
        post.title.toLowerCase().includes(term) ||
        post.summary.toLowerCase().includes(term) ||
        (post.content && post.content.toLowerCase().includes(term))
      );
    });

    render(matches, term);
  });
}
"""


def render_post_page(post: Post) -> str:
    canonical = _absolute_url(post.url)
    if post.tags:
        tag_markup = "标签 " + " ".join(
            f'<a href="../tags.html#{_tag_slug(tag)}">{escape(tag)}</a>' for tag in post.tags
        )
    else:
        tag_markup = "标签 无"
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
    <div class="page-shell" id="top">
      <header class="site-header compact">
        <nav class="top-nav" aria-label="主导航">
          {_brand("../")}
          <div class="nav-links">
{render_post_nav()}
          </div>
        </nav>
      </header>

      <main class="article-page prose has-toc">
{render_article_toc(post)}
        <article class="article-content">
          <h1>{escape(post.title)}</h1>
          <p class="meta article-meta">
            <span>发布于 {post.display_date}</span>
            <span>更新于 {post.display_updated}</span>
            <span>{tag_markup}</span>
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

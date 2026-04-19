from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
OUTPUT_DIR = ROOT / "dist"

SITE_TITLE = "MyBlog"
SITE_DESCRIPTION = (
    "A reading-first blog inspired by Lilian Weng's calm, technical writing style."
)
HOME_EYEBROW = "Personal Notes and Essays"
HOME_HEADING = "Welcome to MyBlog"
HOME_LEDE = (
    "I write about engineering, machine learning, and the systems work "
    "that usually matters more than the demo."
)
SOCIAL_LINKS = [
    ("GitHub", "https://github.com/"),
    ("X", "https://x.com/"),
    ("LinkedIn", "https://www.linkedin.com/"),
]
NAV_LINKS = [
    ("Posts", "index.html"),
    ("Archive", "archive.html"),
    ("Search", "search.html"),
    ("Tags", "tags.html"),
    ("FAQ", "faq.html"),
]


@dataclass
class Post:
    source_path: Path
    slug: str
    title: str
    date: datetime
    summary: str
    read_time: str
    author: str
    tags: list[str]
    body_html: str

    @property
    def url(self) -> str:
        return f"posts/{self.slug}.html"

    @property
    def iso_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def display_date(self) -> str:
        return self.date.strftime("%B %d, %Y").replace(" 0", " ")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("Markdown post must start with frontmatter delimited by ---")

    _, remainder = text.split("---\n", 1)
    try:
        frontmatter_text, body = remainder.split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError("Frontmatter must end with a closing --- line") from exc

    metadata: dict[str, str] = {}
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid frontmatter line: {raw_line}")
        metadata[key.strip()] = value.strip()

    return metadata, body.lstrip()


def parse_tags(value: str) -> list[str]:
    if not value:
        return []
    parts = [item.strip() for item in value.split(",")]
    return [item for item in parts if item]


def slugify(path: Path) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", path.stem.lower()).strip("-")


def render_inline(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_code_block = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code_block:
                code_html = escape("\n".join(code_lines))
                blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h3>{render_inline(stripped[4:])}</h3>")
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{render_inline(stripped[3:])}</h2>")
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h1>{render_inline(stripped[2:])}</h1>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()

    if in_code_block:
        code_html = escape("\n".join(code_lines))
        blocks.append(f"<pre><code>{code_html}</code></pre>")

    return "\n          ".join(blocks)


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        slug = metadata.get("slug", "").strip() or slugify(path)
        title = metadata["title"]
        date = datetime.strptime(metadata["date"], "%Y-%m-%d")
        summary = metadata["summary"]
        read_time = metadata.get("read_time", "5 min")
        author = metadata.get("author", "You")
        tags = parse_tags(metadata.get("tags", ""))
        posts.append(
            Post(
                source_path=path,
                slug=slug,
                title=title,
                date=date,
                summary=summary,
                read_time=read_time,
                author=author,
                tags=tags,
                body_html=markdown_to_html(body),
            )
        )

    return sorted(posts, key=lambda post: post.date, reverse=True)


def render_nav(current_href: str) -> str:
    links: list[str] = []
    for label, href in NAV_LINKS:
        current = ' aria-current="page"' if href == current_href else ""
        links.append(f'            <a href="{href}"{current}>{label}</a>')
    return "\n".join(links)


def render_post_nav() -> str:
    return "\n".join(f'            <a href="../{href}">{label}</a>' for label, href in NAV_LINKS)


def render_layout(title: str, content: str, current_href: str, description: str = "") -> str:
    meta_description = description or SITE_DESCRIPTION
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(meta_description)}" />
    <link rel="stylesheet" href="assets/style.css" />
  </head>
  <body>
    <div class="page-shell">
{content}
    </div>
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
          <p class="meta">Date: {post.display_date} | Estimated Reading Time: {escape(post.read_time)} | Author: {escape(post.author)}</p>
        </article>"""
        )

    socials = "\n".join(
        f'            <a href="{href}" target="_blank" rel="noreferrer">{escape(label)}</a>'
        for label, href in SOCIAL_LINKS
    )

    content = f"""      <header class="site-header">
        <nav class="top-nav" aria-label="Primary">
          <a class="brand" href="index.html">{SITE_TITLE}</a>
          <div class="nav-links">
{render_nav("index.html")}
          </div>
        </nav>
        <section class="hero">
          <p class="eyebrow">{HOME_EYEBROW}</p>
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

    return render_layout(SITE_TITLE, content, "index.html", SITE_DESCRIPTION)


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
    return render_layout(f"Archive | {SITE_TITLE}", content, "archive.html")


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
    return render_layout(f"Tags | {SITE_TITLE}", content, "tags.html")


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
    return render_layout(f"Search | {SITE_TITLE}", content, "search.html")


def render_faq_page() -> str:
    content = f"""{render_page_header("faq.html", "FAQ")}

      <main class="content-page prose">
        <h2>What is this blog for?</h2>
        <p>Long-form notes, technical essays, and project writeups.</p>
        <h2>How is it deployed?</h2>
        <p>As a static site on GitHub Pages through a GitHub Actions workflow.</p>
        <h2>How do I publish new posts?</h2>
        <p>Write a new Markdown file in <code>posts/</code> with frontmatter, then push to <code>main</code>. GitHub Actions will generate the HTML pages automatically.</p>
      </main>"""
    return render_layout(f"FAQ | {SITE_TITLE}", content, "faq.html")


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
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(post.title)} | {SITE_TITLE}</title>
    <meta name="description" content="{escape(post.summary)}" />
    <link rel="stylesheet" href="../assets/style.css" />
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
          <p class="meta">Date: {post.display_date} | Estimated Reading Time: {escape(post.read_time)} | Author: {escape(post.author)}</p>
          {post.body_html}
        </article>
      </main>
    </div>
  </body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    posts = load_posts()
    if not posts:
        raise SystemExit("No Markdown posts found in posts/")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(ROOT / "assets", OUTPUT_DIR / "assets")

    write_text(OUTPUT_DIR / "index.html", render_home(posts))
    write_text(OUTPUT_DIR / "archive.html", render_archive(posts))
    write_text(OUTPUT_DIR / "tags.html", render_tags(posts))
    write_text(OUTPUT_DIR / "search.html", render_search_page())
    write_text(OUTPUT_DIR / "faq.html", render_faq_page())
    write_text(OUTPUT_DIR / "assets" / "search.js", render_search_index(posts))

    for post in posts:
        write_text(OUTPUT_DIR / "posts" / f"{post.slug}.html", render_post_page(post))


if __name__ == "__main__":
    main()

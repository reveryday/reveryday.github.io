from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
OUTPUT_DIR = ROOT / "dist"

SITE_TITLE = "Wens'Blog"
SITE_DESCRIPTION = "Wens' personal blog about nuclear energy, machine learning, and technical notes."
HEAD_EXTRAS = """
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/github.min.css"
    />
"""
FOOTER_SCRIPTS = """
    <script
      defer
      src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"
    ></script>
    <script
      defer
      src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
      onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\\\[',right:'\\\\]',display:true},{left:'$',right:'$',display:false},{left:'\\\\(',right:'\\\\)',display:false}]});"
    ></script>
    <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/highlight.min.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", () => {
        if (window.hljs) {
          window.hljs.highlightAll();
        }
      });
    </script>
"""
HOME_HEADING = "Welcome to my world!"
HOME_LEDE = (
    "A blog about nuclear energy, machine learning, and technical notes. I write about things I'm learning, projects I'm working on, and topics."
)
SOCIAL_LINKS = [
    #("X", "https://x.com/"),
    #("LinkedIn", "https://www.linkedin.com/"),
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
    updated: datetime
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

    @property
    def display_updated(self) -> str:
        return self.updated.strftime("%B %d, %Y").replace(" 0", " ")

    @property
    def display_tags(self) -> str:
        return ", ".join(self.tags) if self.tags else "None"


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
    stem = unicodedata.normalize("NFKC", path.stem).strip().lower()
    stem = stem.replace("_", "-").replace(" ", "-")
    stem = re.sub(r"[^\w\-]+", "-", stem, flags=re.UNICODE)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return stem or "post"


def parse_date(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def stash_token(store: list[str], html: str) -> str:
    token = f"@@TOKEN{len(store)}@@"
    store.append(html)
    return token


def restore_tokens(text: str, store: list[str]) -> str:
    for index, value in enumerate(store):
        text = text.replace(f"@@TOKEN{index}@@", value)
    return text


def normalize_image_html(source: str, alt: str = "", style: str = "") -> str:
    normalized_style = style.strip()
    zoom_match = re.search(r"zoom\s*:\s*([\d.]+)%", normalized_style, re.IGNORECASE)
    if zoom_match:
        normalized_style = re.sub(
            r"zoom\s*:\s*[\d.]+%\s*;?",
            f"width: {zoom_match.group(1)}%;",
            normalized_style,
            flags=re.IGNORECASE,
        ).strip()

    style_attr = f' style="{escape(normalized_style, quote=True)}"' if normalized_style else ""
    caption = f"<figcaption>{escape(alt)}</figcaption>" if alt else ""
    return f'<figure class="prose-figure"><img src="{escape(source, quote=True)}" alt="{escape(alt, quote=True)}" loading="lazy"{style_attr} />{caption}</figure>'


def parse_image_attributes(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""

    parts = re.split(r"\s+", raw)
    styles: list[str] = []
    for part in parts:
        key, sep, value = part.partition("=")
        if not sep:
            continue
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        if key in {"width", "height", "max-width"} and value:
            styles.append(f"{key}: {value};")
    return " ".join(styles)


def render_inline(text: str) -> str:
    stored: list[str] = []

    def keep_raw_html(match: re.Match[str]) -> str:
        return stash_token(stored, match.group(0))

    def keep_inline_code(match: re.Match[str]) -> str:
        return stash_token(stored, f"<code>{escape(match.group(1))}</code>")

    def keep_inline_math(match: re.Match[str]) -> str:
        return stash_token(stored, f"\\({match.group(1).strip()}\\)")

    text = re.sub(r"<img\s+[^>]*?/?>", keep_raw_html, text)
    text = re.sub(r"`([^`]+)`", keep_inline_code, text)
    text = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", keep_inline_math, text)

    escaped = escape(text)

    def render_image(match: re.Match[str]) -> str:
        alt = escape(match.group(1))
        src = escape(match.group(2), quote=True)
        return f'<img src="{src}" alt="{alt}" loading="lazy" />'

    def render_link(match: re.Match[str]) -> str:
        label = match.group(1)
        href = escape(match.group(2), quote=True)
        return f'<a href="{href}">{label}</a>'

    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", render_image, escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", render_link, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return restore_tokens(escaped, stored)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_kind: str | None = None
    in_code_block = False
    code_lines: list[str] = []
    code_language = ""
    in_display_math = False
    math_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, list_kind
        if list_items:
            items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
            tag = "ol" if list_kind == "ol" else "ul"
            blocks.append(f"<{tag}>{items}</{tag}>")
            list_items = []
            list_kind = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code_block:
                code_html = escape("\n".join(code_lines))
                language_class = f' class="language-{escape(code_language)}"' if code_language else ""
                blocks.append(f"<pre><code{language_class}>{code_html}</code></pre>")
                code_lines = []
                code_language = ""
                in_code_block = False
            else:
                in_code_block = True
                code_language = stripped[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped == "$$":
            flush_paragraph()
            flush_list()
            if in_display_math:
                blocks.append(
                    '<div class="math-display">\\[' + "\n".join(math_lines).strip() + "\\]</div>"
                )
                math_lines = []
                in_display_math = False
            else:
                in_display_math = True
            continue

        if in_display_math:
            math_lines.append(line)
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

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<blockquote><p>{render_inline(stripped[2:])}</p></blockquote>")
            continue

        ordered_match = re.match(r"(\d+)\.\s+(.+)", stripped)
        if ordered_match:
            flush_paragraph()
            if list_kind not in (None, "ol"):
                flush_list()
            list_kind = "ol"
            list_items.append(ordered_match.group(2).strip())
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if list_kind not in (None, "ul"):
                flush_list()
            list_kind = "ul"
            list_items.append(stripped[2:].strip())
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)(?:\s*\{([^}]+)\})?", stripped)
        if image_match:
            flush_paragraph()
            flush_list()
            blocks.append(
                normalize_image_html(
                    image_match.group(2),
                    image_match.group(1),
                    parse_image_attributes(image_match.group(3) or ""),
                )
            )
            continue

        if stripped.lower().startswith("<img "):
            flush_paragraph()
            flush_list()
            src_match = re.search(r'src="([^"]+)"', stripped, re.IGNORECASE)
            alt_match = re.search(r'alt="([^"]*)"', stripped, re.IGNORECASE)
            style_match = re.search(r'style="([^"]*)"', stripped, re.IGNORECASE)
            if src_match:
                blocks.append(
                    normalize_image_html(
                        src_match.group(1),
                        alt_match.group(1) if alt_match else "",
                        style_match.group(1) if style_match else "",
                    )
                )
            else:
                blocks.append(stripped)
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()

    if in_code_block:
        code_html = escape("\n".join(code_lines))
        language_class = f' class="language-{escape(code_language)}"' if code_language else ""
        blocks.append(f"<pre><code{language_class}>{code_html}</code></pre>")

    if in_display_math:
        blocks.append('<div class="math-display">\\[' + "\n".join(math_lines).strip() + "\\]</div>")

    return "\n          ".join(blocks)


def extract_summary(markdown: str, limit: int = 160) -> str:
    lines: list[str] = []
    in_code_block = False

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("![](") or stripped.startswith("!["):
            continue
        if stripped.startswith("<img"):
            continue

        cleaned = re.sub(r"`([^`]+)`", r"\1", stripped)
        cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", cleaned)
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
        cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)
        cleaned = re.sub(r"<[^>]+>", "", cleaned).strip()
        if cleaned:
            lines.append(cleaned)
        if lines:
            break

    summary = " ".join(lines).strip()
    if len(summary) > limit:
        summary = summary[: limit - 1].rstrip() + "..."
    return summary or "No summary yet."


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        slug = metadata.get("slug", "").strip() or slugify(path)
        title = metadata["title"]
        date = parse_date(metadata["date"])
        updated = parse_date(metadata["updated"]) if metadata.get("updated") else date
        summary = metadata.get("summary", "").strip() or extract_summary(body)
        read_time = metadata.get("read_time", "5 min")
        author = metadata.get("author", "Wens")
        tags = parse_tags(metadata.get("tags", ""))
        posts.append(
            Post(
                source_path=path,
                slug=slug,
                title=title,
                date=date,
                updated=updated,
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
    eyebrow = globals().get("HOME_EYEBROW", "").strip()
    eyebrow_html = f'          <p class="eyebrow">{escape(eyebrow)}</p>\n' if eyebrow else ""

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


def main() -> None:
    posts = load_posts()
    if not posts:
        raise SystemExit("No Markdown posts found in posts/")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_static_assets(ROOT / "assets", OUTPUT_DIR / "assets")

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

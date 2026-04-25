from __future__ import annotations

import re
from html import escape


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
    return (
        f'<figure class="prose-figure"><img src="{escape(source, quote=True)}" '
        f'alt="{escape(alt, quote=True)}" loading="lazy"{style_attr} />{caption}</figure>'
    )


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
        return stash_token(stored, f"\\({escape(match.group(1).strip())}\\)")

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

    list_kind: str | None = None
    list_items: list[list[str]] = []
    list_start_number: int = 1

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
        nonlocal list_items, list_kind, list_start_number
        if not list_items:
            return

        rendered_items = []
        for item_lines in list_items:
            if not item_lines:
                continue

            content_lines = list(item_lines)
            min_indent = 999
            for item_line in content_lines[1:]:
                if item_line.strip():
                    min_indent = min(min_indent, len(item_line) - len(item_line.lstrip()))

            if min_indent != 999 and min_indent > 0:
                for index in range(1, len(content_lines)):
                    if len(content_lines[index]) >= min_indent:
                        content_lines[index] = content_lines[index][min_indent:]
                    elif not content_lines[index].strip():
                        content_lines[index] = ""
                    else:
                        content_lines[index] = content_lines[index].lstrip()

            item_html = markdown_to_html("\n".join(content_lines).strip())
            rendered_items.append(f"<li>{item_html}</li>")

        tag = "ol" if list_kind == "ol" else "ul"
        start_attr = (
            f' start="{list_start_number}"' if list_kind == "ol" and list_start_number != 1 else ""
        )
        blocks.append(f"<{tag}{start_attr}>{''.join(rendered_items)}</{tag}>")
        list_items = []
        list_kind = None
        list_start_number = 1

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if list_kind and not in_code_block and not in_display_math:
            is_list_continuation = False

            if indent >= 2:
                is_list_continuation = True
            elif not stripped:
                next_non_empty = -1
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        next_non_empty = j
                        break
                if next_non_empty != -1:
                    next_line = lines[next_non_empty]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent >= 2 or re.match(r"^(\d+)\.\s+", next_line.lstrip()) or next_line.lstrip().startswith("- "):
                        is_list_continuation = True

            if is_list_continuation:
                list_items[-1].append(line)
                i += 1
                continue

        ol_match = re.match(r"^(\d+)\.\s+(.*)", line.lstrip())
        ul_match = re.match(r"^- (.*)", line.lstrip())

        if not in_code_block and not in_display_math and (ol_match or ul_match) and indent < 4:
            flush_paragraph()
            kind = "ol" if ol_match else "ul"
            content = ol_match.group(2) if ol_match else ul_match.group(1)
            num = int(ol_match.group(1)) if ol_match else 1

            if list_kind and list_kind != kind:
                flush_list()

            if not list_kind:
                list_kind = kind
                list_start_number = num

            list_items.append([content])
            i += 1
            continue

        if list_kind and not in_code_block and not in_display_math:
            flush_list()

        if in_code_block:
            if stripped.startswith("```"):
                code_html = escape("\n".join(code_lines))
                lang_class = f' class="language-{escape(code_language)}"' if code_language else ""
                blocks.append(f"<pre><code{lang_class}>{code_html}</code></pre>")
                code_lines = []
                code_language = ""
                in_code_block = False
            else:
                code_lines.append(line)
            i += 1
            continue

        if in_display_math:
            if stripped == "$$":
                blocks.append('<div class="math-display">\\[' + escape("\n".join(math_lines).strip()) + "\\]</div>")
                math_lines = []
                in_display_math = False
            else:
                math_lines.append(line)
            i += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            in_code_block = True
            code_language = stripped[3:].strip()
            i += 1
            continue

        if stripped == "$$":
            flush_paragraph()
            in_display_math = True
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        if re.fullmatch(r"(?:-{3,}|\*{3,}|_{3,})", stripped):
            flush_paragraph()
            flush_list()
            blocks.append("<hr />")
            i += 1
            continue

        if stripped.startswith("#### "):
            flush_paragraph()
            blocks.append(f"<h4>{render_inline(stripped[5:])}</h4>")
            i += 1
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            blocks.append(f"<h3>{render_inline(stripped[4:])}</h3>")
            i += 1
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            blocks.append(f"<h2>{render_inline(stripped[3:])}</h2>")
            i += 1
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            blocks.append(f"<h1>{render_inline(stripped[2:])}</h1>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            quote_text = stripped[1:].lstrip()
            blocks.append(f"<blockquote><p>{render_inline(quote_text)}</p></blockquote>")
            i += 1
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
            i += 1
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
            i += 1
            continue

        if re.match(r"^<p(?:\s+[^>]*)?>$", stripped, re.IGNORECASE) or re.match(
            r"^<p(?:\s+[^>]*)?>.*</p>$", stripped, re.IGNORECASE
        ):
            flush_paragraph()
            flush_list()

            raw_html_lines = [line]
            if not re.search(r"</p>$", stripped, re.IGNORECASE):
                i += 1
                while i < len(lines):
                    raw_html_lines.append(lines[i])
                    if re.search(r"</p>\s*$", lines[i].strip(), re.IGNORECASE):
                        break
                    i += 1

            blocks.append("\n".join(raw_html_lines))
            i += 1
            continue

        if list_kind:
            flush_list()
        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    flush_list()
    if in_code_block:
        code_html = escape("\n".join(code_lines))
        lang_class = f' class="language-{escape(code_language)}"' if code_language else ""
        blocks.append(f"<pre><code{lang_class}>{code_html}</code></pre>")
    if in_display_math:
        blocks.append('<div class="math-display">\\[' + escape("\n".join(math_lines).strip()) + "\\]</div>")
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

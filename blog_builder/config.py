from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
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
    <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/languages/fortran.min.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", () => {
        if (window.hljs) {
          window.hljs.highlightAll();
        }
      });
    </script>
"""
HOME_HEADING = "Welcome to my world."
HOME_LEDE = " I write about what I am learning, building, and figuring out along the way, from technical notes and project write-ups to ideas that are still taking shape."
HOME_EYEBROW = ""
SOCIAL_LINKS = [
    # ("X", "https://x.com/"),
    # ("LinkedIn", "https://www.linkedin.com/"),
]
NAV_LINKS = [
    ("Posts", "index.html"),
    ("Archive", "archive.html"),
    ("Search", "search.html"),
    ("Playground", "playground.html"),
    ("Tags", "tags.html"),
    ("Friends", "friends.html"),
    ("FAQ", "faq.html"),
]

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
PAGES_DIR = ROOT / "pages"
OUTPUT_DIR = ROOT / "dist"

SITE_TITLE = "Wens'Blog"
SITE_DESCRIPTION = "Wens' personal blog about nuclear energy, machine learning, and technical notes."
SITE_BASE_URL = "https://reveryday.github.io/"
SITE_AUTHOR = "Wens"
HEAD_EXTRAS = """
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
    />
    <link
      id="hljs-light"
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/github.min.css"
      media="(prefers-color-scheme: light)"
    />
    <link
      id="hljs-dark"
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/github-dark.min.css"
      media="(prefers-color-scheme: dark)"
    />
    <script>
      window.__setTheme = function (theme) {
        document.documentElement.setAttribute("data-theme", theme);
        var l = document.getElementById("hljs-light");
        var d = document.getElementById("hljs-dark");
        if (l) l.media = theme === "dark" ? "not all" : "all";
        if (d) d.media = theme === "dark" ? "all" : "not all";
      };
      try {
        var stored = localStorage.getItem("theme");
        if (stored === "dark" || stored === "light") window.__setTheme(stored);
      } catch (e) {}
    </script>
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
    <script>
      (function () {
        function effective() {
          var t = document.documentElement.getAttribute("data-theme");
          if (t === "dark" || t === "light") return t;
          return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "theme-toggle";
        function sync() {
          var dark = effective() === "dark";
          btn.textContent = dark ? "\\u2600" : "\\u263e";
          btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
          btn.setAttribute("aria-pressed", String(dark));
        }
        sync();
        btn.addEventListener("click", function () {
          var next = effective() === "dark" ? "light" : "dark";
          if (window.__setTheme) window.__setTheme(next);
          try { localStorage.setItem("theme", next); } catch (e) {}
          sync();
        });
        document.body.appendChild(btn);
      })();
    </script>
"""
HOME_HEADING = "天道酬勤"
HOME_LEDE = ""
HOME_EYEBROW = ""
SOCIAL_LINKS = [
    # ("X", "https://x.com/"),
    # ("LinkedIn", "https://www.linkedin.com/"),
]
NAV_LINKS = [
    ("首页", "index.html"),
    ("归档", "archive.html"),
    ("搜索", "search.html"),
    ("标签", "tags.html"),
    ("收藏", "collection.html"),
    ("友链", "friends.html"),
]

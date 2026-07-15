from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
PAGES_DIR = ROOT / "pages"
OUTPUT_DIR = ROOT / "dist"

POSTS_PER_PAGE = 8

SITE_TITLE = "Wens'Blog"
SITE_DESCRIPTION = "Wens 的个人博客，记录核能、机器学习、编程与日常思考。"
SITE_BASE_URL = "https://reveryday.github.io/"
SITE_AUTHOR = "Wens"
HEAD_EXTRAS = """
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
        var btn = document.querySelector(".theme-toggle");
        if (!btn) return;
        var sunIcon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3.5"/><path d="M12 2.5v2m0 15v2m9.5-9.5h-2m-15 0h-2m16.2-6.7-1.4 1.4M6.7 17.3l-1.4 1.4m13.4 0-1.4-1.4M6.7 6.7 5.3 5.3"/></svg>';
        var moonIcon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 15.2A8.5 8.5 0 0 1 8.8 4a8.5 8.5 0 1 0 11.2 11.2Z"/></svg>';
        function sync() {
          var dark = effective() === "dark";
          btn.innerHTML = dark ? sunIcon : moonIcon;
          btn.setAttribute("aria-label", dark ? "切换浅色模式" : "切换深色模式");
          btn.setAttribute("aria-pressed", String(dark));
        }
        sync();
        btn.addEventListener("click", function () {
          try {
            document.documentElement.classList.add("theme-transition");
            window.clearTimeout(window.__themeTransitionTimer);
            window.__themeTransitionTimer = window.setTimeout(function () {
              document.documentElement.classList.remove("theme-transition");
            }, 360);
          } catch (e) {}
          var next = effective() === "dark" ? "light" : "dark";
          if (window.__setTheme) window.__setTheme(next);
          try { localStorage.setItem("theme", next); } catch (e) {}
          sync();
        });
      })();
    </script>
    <script>
      (function () {
        var bar = document.createElement("div");
        bar.className = "reading-progress";
        document.body.appendChild(bar);
        var root = document.documentElement;
        function update() {
          var max = root.scrollHeight - root.clientHeight;
          var pct = max > 0 ? root.scrollTop / max : 0;
          bar.style.transform = "scaleX(" + pct + ")";
        }
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        update();
      })();
      (function () {
        var prose = document.querySelector(".prose");
        if (!prose) return;
        var heads = prose.querySelectorAll("h2[id], h3[id], h4[id]");
        for (var k = 0; k < heads.length; k++) {
          var link = document.createElement("a");
          link.className = "heading-anchor";
          link.href = "#" + heads[k].id;
          link.setAttribute("aria-label", "链接到本节");
          link.innerHTML = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m10.5 13.5 3-3"/><path d="M7.8 15.8 6.4 17.2a3.4 3.4 0 0 1-4.8-4.8L5 9a3.4 3.4 0 0 1 4.8 0"/><path d="m16.2 8.2 1.4-1.4a3.4 3.4 0 1 1 4.8 4.8L19 15a3.4 3.4 0 0 1-4.8 0"/></svg>';
          heads[k].appendChild(link);
        }
      })();
      (function () {
        var toc = document.querySelector(".article-toc");
        if (!toc || !("IntersectionObserver" in window)) return;
        var links = toc.querySelectorAll('a[href^="#"]');
        if (!links.length) return;
        var map = {};
        var targets = [];
        for (var i = 0; i < links.length; i++) {
          var id = decodeURIComponent(links[i].getAttribute("href").slice(1));
          var el = document.getElementById(id);
          if (el) { map[id] = links[i]; targets.push(el); }
        }
        if (!targets.length) return;
        var current = null;
        function setActive(a) {
          if (current === a) return;
          if (current) current.removeAttribute("aria-current");
          if (a) a.setAttribute("aria-current", "true");
          current = a;
        }
        var observer = new IntersectionObserver(function (entries) {
          for (var j = 0; j < entries.length; j++) {
            if (entries[j].isIntersecting) {
              var a = map[entries[j].target.id];
              if (a) setActive(a);
            }
          }
        }, { rootMargin: "-12% 0px -75% 0px", threshold: 0 });
        for (var t = 0; t < targets.length; t++) observer.observe(targets[t]);
      })();
    </script>
"""
HOME_HEADING = "希望无所谓能天天开心"
NAV_LINKS = [
    ("首页", "index.html"),
    ("归档", "archive.html"),
    ("收藏", "collection.html"),
    ("友链", "friends.html"),
]

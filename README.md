# MyBlog

一个用 Python 写的静态博客生成器。文章放在 `posts/`，执行 `python build.py` 后生成 `dist/`，可直接本地打开，也可部署到 GitHub Pages。

## 目录

- `posts/`：Markdown 文章
- `assets/`：静态资源
- `blog_builder/`：构建逻辑
- `build.py`：构建入口
- `dist/`：生成后的站点

## 本地构建

```bash
python build.py
```

构建完成后直接打开 `dist/index.html` 即可预览。

## 写文章

在 `posts/` 下新建 `*.md` 文件，示例：

```md
---
title: My New Post
date: 2026-04-26
summary: A short summary shown on the homepage and search page.
tags: Notes, Writing
sticky: 0
published: true
---

Your content starts here.
```

当前常用字段：

- `title`：标题，必填
- `date`：日期，必填，支持 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- `summary`：摘要，可选
- `tags`：标签，多个标签用逗号分隔
- `sticky`：置顶权重，可选
- `published`：设为 `false` 时不会生成页面
- `slug`：自定义文章链接，可选

## 支持的内容

- 标题、段落、列表、引用、代码块
- 行内公式 `$...$` 和块级公式 `$$...$$`
- Markdown 图片
- 带尺寸的图片：`![alt](url){ width=50% }`
- 原生 HTML `img`，支持将 `zoom` 转成宽度

## 生成结果

构建后会自动生成：

- `dist/index.html`
- `dist/archive.html`
- `dist/tags.html`
- `dist/search.html`
- `dist/faq.html`
- `dist/friends.html`
- `dist/posts/*.html`
- `dist/assets/search.js`

## 部署

仓库已包含 GitHub Pages workflow：`.github/workflows/deploy.yml`

推送到 `main` 后会自动执行：

```bash
python build.py
```

并将 `dist/` 部署到 GitHub Pages。

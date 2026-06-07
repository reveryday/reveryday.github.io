from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TocItem:
    level: int
    title: str
    anchor: str


@dataclass
class Post:
    slug: str
    title: str
    date: datetime
    updated: datetime
    sticky: int
    summary: str
    tags: list[str]
    body_html: str
    toc: list[TocItem]

    @property
    def url(self) -> str:
        return f"posts/{self.slug}.html"

    @property
    def iso_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def display_date(self) -> str:
        return f"{self.date.year}年{self.date.month}月{self.date.day}日"

    @property
    def display_updated(self) -> str:
        return f"{self.updated.year}年{self.updated.month}月{self.updated.day}日"

    @property
    def display_tags(self) -> str:
        return ", ".join(self.tags) if self.tags else "无"

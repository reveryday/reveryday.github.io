from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


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

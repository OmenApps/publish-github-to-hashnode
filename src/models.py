"""Domain models for blog posts."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PostMetadata:
    """Post metadata from frontmatter."""

    title: str
    subtitle: Optional[str] = None
    slug: Optional[str] = None
    tags: list[dict[str, str]] = None
    publishedAt: Optional[str] = None
    coverImage: Optional[str] = None
    coverImageAttribution: Optional[str] = None
    enableTableOfContents: bool = False
    delisted: bool = False
    disableComments: bool = False


@dataclass
class Post:
    """Domain model for a blog post."""

    file_path: Path
    metadata: PostMetadata
    content: str
    publication_id: str

    @property
    def slug(self) -> str:
        """Get post slug, generating from title if not set."""
        return self.metadata.slug or self._generate_slug(self.metadata.title)

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generate a URL-friendly slug from a title."""
        return "-".join(title.strip().lower().split())

"""Process markdown files for publication."""
import re
from pathlib import Path
from typing import Any

import frontmatter

from .exceptions import InvalidPostError
from .models import Post, PostMetadata


class MarkdownProcessor:
    """Process markdown files for publication."""

    def __init__(self, publication_id: str, github_raw_url: str, repository: str, branch: str):
        self.publication_id = publication_id
        self.github_raw_url = github_raw_url
        self.repository = repository
        self.branch = branch

    def process_file(self, file_path: Path) -> Post:
        """Process a markdown file into a Post domain object."""
        metadata, content = self._read_file(file_path)
        self._validate_content(content)

        processed_content = self._process_content(content, file_path)
        post_metadata = self._process_metadata(metadata)

        return Post(
            file_path=file_path, metadata=post_metadata, content=processed_content, publication_id=self.publication_id
        )

    def _read_file(self, file_path: Path) -> tuple[dict[str, Any], str]:
        """Read and parse a markdown file."""
        with file_path.open("r") as f:
            post = frontmatter.load(f)
        return post.metadata, post.content

    def _validate_content(self, content: str) -> None:
        """Ensure content is not empty."""
        if not content.strip():
            raise InvalidPostError("Post content cannot be empty")

    def _process_metadata(self, metadata: dict[str, Any]) -> PostMetadata:
        """Process and validate metadata."""
        if "title" not in metadata:
            raise InvalidPostError("Post must have a title")

        # Process tags if they exist
        if "tags" in metadata:
            metadata["tags"] = [
                {"slug": tag.strip().lower(), "name": tag.strip()} for tag in metadata["tags"].split(",")
            ]

        return PostMetadata(**metadata)

    def _process_content(self, content: str, file_path: Path) -> str:
        """Process content, updating image URLs to absolute paths."""
        relative_image_regex = re.compile(r"!\[(.*?)\]\((?!http)(.*?)\)")
        return relative_image_regex.sub(
            lambda m: f"![{m.group(1)}]({self._get_resource_url(file_path.parent / m.group(2))})",
            content,
        )

    def _get_resource_url(self, path: Path) -> str:
        """Get the absolute URL for a resource in the GitHub repository."""
        return f"{self.github_raw_url}/{self.repository}/{self.branch}/{path.as_posix()}"

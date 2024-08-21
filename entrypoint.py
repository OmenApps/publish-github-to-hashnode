"""Publish markdown post files to Hashnode publications.

The script is designed to be used as part of a GitHub Action. It reads the following
environment variables:

- ACCESS_TOKEN: A Hashnode API access token.
- POSTS_DIRECTORY: The directory containing the markdown files to publish. (default: "")
- PUBLICATION_HOST: The host of the Hashnode publication to publish to. (e.g., "my.site.com")
- GITHUB_REPOSITORY: The GitHub repository in the format "owner/repo".
- GITHUB_REF: The branch or tag ref that triggered the action.
- CHANGED_FILES: A JSON object containing the files that were added, modified, or deleted.

Markdown files in the POSTS_DIRECTORY are read and published to the specified Hashnode
publication. Frontmatter fields and post content are extracted from the markdown files.

The script writes the results of the operation to GITHUB_OUTPUT in the format "result_json"
and "result_summary".

Hashnode GraphQL API is used to interact with the Hashnode platform.
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from zoneinfo import ZoneInfo

import frontmatter

from constants import (
    ADDED_FILES,
    ALL_CHANGED_FILES,
    BRANCH,
    CHANGED_FILES,
    GITHUB_OUTPUT,
    GITHUB_RAW_URL,
    GITHUB_REPOSITORY,
    POSTS_DIRECTORY,
)
from graphql import HashnodeAPI

debug_data: List[str] = []
results: Dict[str, Any] = {
    "input_added_files": [str(f) for f in ADDED_FILES],
    "input_files": [str(f) for f in CHANGED_FILES],
    "added": [],
    "modified": [],
    "deleted": [],
    "errors": [],
}


class MarkdownFileHandler:  # pylint: disable=R0903
    """Handle markdown files and prepare data for Hashnode publication."""

    REQUIRED_FIELDS = ["title"]

    def __init__(self, file_path: Path, publication_id: str) -> None:
        self.file_path = file_path
        self.publication_id = publication_id
        self.metadata, self.content = self._process_markdown()
        self._validate()

    def _process_markdown(self) -> Tuple[Dict[str, Any], str]:
        """Extract metadata and content from a markdown file."""
        with self.file_path.open("r") as f:
            post = frontmatter.load(f)
        debug_data.append(f"Processed Markdown: {post.metadata}")
        return post.metadata, post.content

    def _validate(self) -> None:
        """Validate that the content and frontmatter are correct."""
        self._validate_content()
        self._validate_frontmatter()

    def _validate_content(self) -> None:
        """Ensure content is not empty."""
        if not self.content.strip():
            raise ValueError("Content cannot be empty")

    def _validate_frontmatter(self) -> None:
        """Ensure the frontmatter contains the required fields and correct formats."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.metadata:
                raise ValueError(f"Missing required frontmatter field: {field}")

        self.metadata["slug"] = self._generate_slug(self.metadata.get("slug", self.metadata["title"]))
        self.metadata["tags"] = self._process_tags(self.metadata.get("tags", ""))
        self.metadata["publishedAt"] = self._get_publish_date(self.metadata.get("publishedAt"))

        debug_data.append(f"Validated Frontmatter: {self.metadata}")

    def _generate_slug(self, title: str) -> str:
        """Generate a slug from the title."""
        return re.sub(r"\s+", "-", title.strip().lower())

    def _process_tags(self, tags: str) -> List[Dict[str, str]]:
        """Process tags into a list of dictionaries."""
        if not isinstance(tags, str):
            raise ValueError("Tags must be a comma-separated string")
        return [{"slug": tag.strip().lower(), "name": tag.strip()} for tag in tags.split(",")]

    def _get_publish_date(self, published_at: str = None) -> str:
        """Return the publish date, defaulting to now if not provided."""
        if published_at:
            return published_at
        return datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

    def build_post_data(self) -> Dict[str, Any]:
        """Build the post data for the Hashnode API."""
        self._update_image_urls()

        return {
            "title": self.metadata["title"],
            "subtitle": self.metadata.get("subtitle"),
            "publicationId": self.publication_id,
            "contentMarkdown": self.content,
            "publishedAt": self.metadata["publishedAt"],
            "coverImageOptions": {
                "coverImageURL": self._get_cover_image_url(),
                "coverImageAttribution": self.metadata.get("coverImageAttribution"),
            },
            "slug": self.metadata["slug"],
            "tags": self.metadata["tags"],
            "settings": {
                "enableTableOfContent": self.metadata.get("enableTableOfContents", False),
                "delisted": self.metadata.get("delisted", False),
                "slugOverridden": True,
            },
        }

    def _update_image_urls(self) -> None:
        """Update relative image URLs in the content to absolute URLs."""
        relative_image_regex = re.compile(r"!\[(.*?)\]\((?!http)(.*?)\)")
        self.content = relative_image_regex.sub(
            lambda m: f"![{m.group(1)}]({self._get_resource_url(self.file_path.parent / m.group(2))})",
            self.content,
        )

    def _get_cover_image_url(self) -> Union[str, None]:
        """Get the full URL for the cover image if it exists and is a relative path."""
        cover_image = self.metadata.get("coverImage")
        if cover_image and not cover_image.startswith("http"):
            return self._get_resource_url(self.file_path.parent / cover_image)
        return cover_image

    def _get_resource_url(self, path: Path) -> str:
        """Get the URL for a resource in the GitHub repository."""
        return f"{GITHUB_RAW_URL}/{GITHUB_REPOSITORY}/{BRANCH}/{path.as_posix()}"


def get_markdown_files(directory: Path) -> List[Path]:
    """Get a list of all markdown files in the specified directory."""
    if not directory.is_dir():
        raise ValueError(f"Directory not found: {directory}")
    return list(directory.rglob("*.md"))


def handle_post(file_path: Path) -> None:
    """Handle a markdown post file."""
    debug_data.append(f"Handling Post for file: {file_path}")

    api = HashnodeAPI()
    markdown_file_handler = MarkdownFileHandler(file_path, api.publication_id)
    post_data = markdown_file_handler.build_post_data()

    post_id = api.get_post_id(markdown_file_handler.metadata["slug"])
    post_action = "update_post" if post_id else "create_post"

    post = getattr(api, post_action)(post_data)
    if post:
        results["modified" if post_id else "added"].append(post)
    else:
        results["errors"].append({"file": str(file_path), "error": f"Failed to {post_action} post."})

    debug_data.append(f"Completed {post_action} for file: {file_path}")


def handle_deleted_posts(api: HashnodeAPI) -> None:
    """Handle deleted markdown posts by delisting them from the publication."""
    markdown_files = get_markdown_files(Path(POSTS_DIRECTORY))
    slugs = {MarkdownFileHandler(file_path, api.publication_id).metadata["slug"] for file_path in markdown_files}
    posts = api.get_all_publication_posts()

    for post in posts:
        if post["slug"] not in slugs:
            if api.delist_post(post["id"]):
                results["deleted"].append(post)


def create_result_summary() -> str:
    """Create a summary of the results for output."""
    summary = "\n".join(
        f"{action.capitalize()} posts:\n" + "\n".join(f"  - {post['title']} ({post['slug']})" for post in posts)
        for action, posts in results.items()
        if action in ["added", "modified", "deleted"] and posts
    )
    errors = "\n".join(f"  - {error['file']}: {error['error']}" for error in results["errors"])
    return f"{summary}\n\nErrors:\n{errors}\n" if errors else f"{summary}\n\nNo errors.\n"


def write_results_to_github_output() -> None:
    """Write the results to the GitHub output."""
    with open(GITHUB_OUTPUT, "a", encoding="utf-8") as output_file:
        print(f"result_json={json.dumps(results)}", file=output_file)
        delimiter = uuid.uuid1()
        print(f"result_summary<<{delimiter}", file=output_file)
        print(create_result_summary(), file=output_file)
        print(delimiter, file=output_file)


def main() -> None:
    """Main entrypoint for the action."""
    api = HashnodeAPI()
    posts_directory = Path(POSTS_DIRECTORY)

    for file_path in ALL_CHANGED_FILES:
        if file_path.is_relative_to(posts_directory) and file_path.suffix == ".md":
            handle_post(file_path=file_path)
        else:
            results["errors"].append(
                {
                    "file": str(file_path),
                    "error": (
                        "Note: File is not a markdown file or not in the posts directory. "
                        "If you want to publish this file, move it to the posts directory."
                    ),
                }
            )

    handle_deleted_posts(api)
    write_results_to_github_output()


if __name__ == "__main__":
    main()

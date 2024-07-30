"""
Publish markdown post files to Hashnode publications.

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
import os
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
    HEADERS,
    POSTS_DIRECTORY,
)
from graphql import HashnodeAPI

debug_data = []
results = {
    "input_added_files": [str(f) for f in ADDED_FILES],
    "input_files": [str(f) for f in CHANGED_FILES],
    "added": [],
    "modified": [],
    "deleted": [],
    "errors": [],
}


class MarkdownFileHandler:
    """Handle markdown files."""

    def __init__(self, file_path: Path, publication_id: str) -> None:
        self.file_path = file_path
        self.publication_id = publication_id
        self.base_path = file_path.parent
        self.metadata, self.content = self._process_markdown()

        try:
            self._validate_frontmatter()
        except ValueError as e:
            results["errors"].append({"file": str(file_path), "error": str(e)})
            raise ValueError(f"Error processing markdown file: {file_path}") from e

    def _process_markdown(self) -> Tuple[Dict[str, Any], str]:
        """Extract metadata and content from a markdown file."""
        with self.file_path.open("r") as f:
            post = frontmatter.load(f)
        processed_markdown = post.metadata, post.content
        debug_data.append(f"Processed Markdown: {processed_markdown}")
        return processed_markdown

    def _validate_frontmatter(self) -> None:
        """Validate that the frontmatter contains the required fields."""
        required_fields = ["title"]
        for field in required_fields:
            if field not in self.metadata:
                raise ValueError(f"Missing required frontmatter field: {field}")

        # Validate and generate slug
        if "slug" not in self.metadata:
            self.metadata["slug"] = re.sub(r"\s+", "-", self.metadata["title"].strip().lower())
        self.metadata["slug"] = re.sub(r"\s+", "-", self.metadata["slug"].strip().lower())

        # Validate tags
        if "tags" in self.metadata:
            if not isinstance(self.metadata["tags"], str):
                raise ValueError("Tags must be a comma-separated string")
            self.metadata["tags"] = [
                {"slug": tag.strip().lower(), "name": tag.strip()} for tag in self.metadata["tags"].split(",")
            ]
        else:
            self.metadata["tags"] = []

        # Set default publish date to current date
        if "publishedAt" not in self.metadata:
            current_dt = datetime.now(ZoneInfo("UTC"))
            self.metadata["publishedAt"] = current_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        debug_data.append(f"Validated Frontmatter: {self.metadata}")

    def _convert_path_to_posix(self, path: Union[str, Path]) -> str:
        """Convert a path to a POSIX path so it can be used in a URL."""
        return path.as_posix()

    def _get_resource_url(self, path: Path) -> str:
        """Get the URL for a resource in a GitHub repository."""
        return str(f"{GITHUB_RAW_URL}/{GITHUB_REPOSITORY}/{BRANCH}/{self._convert_path_to_posix(path)}")

    def _update_image_urls(self, base_path: Path) -> str:
        """Update relative image URLs in the content."""
        relative_image_regex = re.compile(r"!\[(.*?)\]\((?!http)(.*?)\)")
        self.content = relative_image_regex.sub(
            lambda m: f"![{m.group(1)}]({self._get_resource_url(base_path / m.group(2))})",
            self.content,
        )

    def build_post_data(self, publication_id) -> Dict[str, Any]:
        """Build the post data for the Hashnode API."""

        # Check if inline images are relative paths and convert them to URLs
        self._update_image_urls(self.base_path)

        # Check if cover image is a relative path and convert it to a URL
        if "coverImage" in self.metadata and not self.metadata["coverImage"].startswith("http"):
            self.metadata["coverImage"] = self._get_resource_url(self.base_path / self.metadata["coverImage"])

        post_data = {
            "title": self.metadata["title"],
            "subtitle": self.metadata.get("subtitle"),
            "publicationId": publication_id,
            "contentMarkdown": self.metadata["contentMarkdown"],
            "publishedAt": self.metadata["publishedAt"],
            "coverImageOptions": {
                "coverImageURL": self.metadata.get("coverImage"),
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
        debug_data.append(f"Post Data before create or update: {post_data}")
        return post_data


def get_markdown_files() -> List[Path]:
    """Get a list of all .md files in the posts directory."""
    directory = POSTS_DIRECTORY
    if isinstance(directory, str):
        directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Directory not found: {directory}")

    # Use rglob to find all .md files recursively
    markdown_files = list(directory.rglob("*.md"))

    return markdown_files


def handle_post(  # pylint: disable=too-many-arguments
    file_path: Path,
) -> None:
    """Handle a markdown post file."""

    debug_data.append(
        f"Handling Post with args: {file_path=}, {GITHUB_REPOSITORY=}, {BRANCH=}, "
        f"{len(HEADERS)=}, {results=}, {ADDED_FILES=}"
    )

    api = HashnodeAPI()

    # Get the post data from the markdown file
    markdown_file_handler = MarkdownFileHandler(file_path, api.publication_id)
    post_data = markdown_file_handler.build_post_data(publication_id=api.publication_id)

    debug_data.append(f"Post Data before create or update: {post_data}")

    post_id = api.get_post_id(markdown_file_handler.metadata["slug"])

    # If the post already exists, update it.
    if post_id:
        post_data["id"] = post_id
        post = api.update_post(post_data)
        debug_data.append(api.debug_data)
        results["modified"].append(post)
        debug_data.append(f"Updated Post with id: {post_id}, Post Data: {post_data}")

    # Otherwise, create a new post.
    else:
        post = api.create_post(post_data)
        debug_data.append(api.debug_data)
        results["added"].append(post)
        debug_data.append(f"Created Post with id: {post_id}, Post Data: {post_data}")

    return results


def handle_deleted_posts() -> None:
    """If a post is deleted from the repository, delist (soft-delete) it from the publication."""

    # Get list of all .md files in the posts directory
    markdown_files = get_markdown_files()

    api = HashnodeAPI()

    # Get the slug of each file from the markdown frontmatter as a dict of slug: file_path
    slugs = {}
    for file_path in markdown_files:
        markdown_file_handler = MarkdownFileHandler(file_path, api.publication_id)
        slugs[markdown_file_handler.metadata["slug"]] = file_path

    # Get the list of posts from the publication
    posts = api.get_all_publication_posts()
    debug_data.append(api.debug_data)

    # Compare the slugs of the posts to the slugs of the files
    for post in posts:
        if post["slug"] not in slugs:
            api.delist_post(post["id"])
            results["deleted"].append(post)


def create_result_summary() -> str:
    """Create a text summary of the results."""
    summary = ""

    # Show added, modified, and deleted posts
    for action, posts in results.items():
        if action in ["added", "modified", "deleted"]:
            if posts:
                summary += f"{action.capitalize()} posts:\n"
                for post in posts:
                    summary += f"  - {post['title']} ({post['slug']})\n"
            else:
                summary += f"No {action} posts.\n"

    # Show errors
    if results["errors"]:
        summary += "Errors:\n"
        for error in results["errors"]:
            summary += f"  - {str(error['file'])}: {error['error']}\n"
    else:
        summary += "No errors.\n"

    # Show debug data
    if debug_data:
        summary += "Debug Data:\n"
        for data in debug_data:
            summary += f"  - {str(data)}\n"
    else:
        summary += "No debug data.\n"

    return summary


def write_results_to_github_output() -> None:
    """Write the results to the GitHub output in two different formats."""

    with open(GITHUB_OUTPUT, "a", encoding="utf-8") as output_file:
        print(f"result_json={json.dumps(results)}", file=output_file)

        # Set multiline output
        # See: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#multiline-strings
        # and: https://github.com/orgs/community/discussions/28146#discussioncomment-5638014
        delimiter = uuid.uuid1()
        print(f"result_summary<<{delimiter}", file=output_file)
        print(create_result_summary(), file=output_file)
        print(delimiter, file=output_file)


def main():
    """Main entrypoint for the action."""

    for file_path in ALL_CHANGED_FILES:
        debug_data.append(f"Processing File: {str(file_path)}, Comparing to path {str(POSTS_DIRECTORY)}")
        if file_path.is_relative_to(POSTS_DIRECTORY) and file_path.suffix == ".md":
            handle_post(file_path=file_path)
        else:
            results["errors"].append(
                {"file": str(file_path), "error": "File is not a markdown file or not in the posts directory"}
            )

    write_results_to_github_output()


if __name__ == "__main__":
    main()

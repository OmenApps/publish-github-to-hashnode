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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import frontmatter
import requests

HASHNODE_API_URL = "https://gql.hashnode.com"
GITHUB_RAW_URL = "https://raw.githubusercontent.com"
TIMEOUT = 10


def get_publication_id(host: str, headers: Dict[str, str]) -> str:
    """Get the publication ID for the given host."""
    query = """
    query Publication($host: String!) {
        publication(host: $host) {
            id
        }
    }
    """
    response = requests.post(
        HASHNODE_API_URL,
        json={"query": query, "variables": {"host": host}},
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"]["publication"]["id"]


def get_post_id(publication_id: str, slug: str, headers: Dict[str, str]) -> Optional[str]:
    """Get the post ID for the given publication and slug."""
    query = """
    query GetPost($publicationId: String!, $slug: String!) {
        publication(id: $publicationId) {
            post(slug: $slug) {
                id
            }
        }
    }
    """
    response = requests.post(
        HASHNODE_API_URL,
        json={
            "query": query,
            "variables": {"publicationId": publication_id, "slug": slug},
        },
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    post = response.json()["data"]["publication"]["post"]
    return post["id"] if post else None


def create_or_update_post(post_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, str]:
    """Create or update a post with the given data."""
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post {
                id
                title
                slug
            }
        }
    }
    """
    response = requests.post(
        HASHNODE_API_URL,
        json={"query": mutation, "variables": {"input": post_data}},
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"]["publishPost"]["post"]


def delete_post(post_id: str, headers: Dict[str, str]) -> bool:
    """Delete a post with the given ID."""
    mutation = """
    mutation RemovePost($id: ID!) {
        removePost(id: $id) {
            success
        }
    }
    """
    response = requests.post(
        HASHNODE_API_URL,
        json={"query": mutation, "variables": {"id": post_id}},
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"]["removePost"]["success"]


def process_markdown(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Extract metadata and content from a markdown file."""
    with file_path.open("r") as f:
        post = frontmatter.load(f)
    return post.metadata, post.content


def validate_frontmatter(metadata: Dict[str, Any]) -> None:
    """Validate that the frontmatter contains the required fields."""
    required_fields = ["title"]
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required frontmatter field: {field}")

    # Validate and generate slug
    if "slug" not in metadata:
        metadata["slug"] = re.sub(r"\s+", "-", metadata["title"].strip().lower())
    metadata["slug"] = re.sub(r"\s+", "-", metadata["slug"].strip().lower())

    # Validate tags
    if "tags" in metadata:
        if not isinstance(metadata["tags"], str):
            raise ValueError("Tags must be a comma-separated string")
        metadata["tags"] = [{"slug": tag.strip().lower(), "name": tag.strip()} for tag in metadata["tags"].split(",")]
    else:
        metadata["tags"] = []

    # Set default publish date
    if "publishedAt" not in metadata:
        metadata["publishedAt"] = datetime.now().isoformat()


def convert_path_to_posix(path: Union[str, Path]) -> str:
    """Convert a path to a POSIX path."""
    return path.as_posix()


def get_resource_url(repo: str, branch: str, path: Path) -> str:
    """Get the URL for a resource in a GitHub repository."""
    return f"{GITHUB_RAW_URL}/{repo}/{branch}/{convert_path_to_posix(path)}"


def update_image_urls(content: str, base_path: Path, repo: str, branch: str) -> str:
    """Update relative image URLs in the content."""
    relative_image_regex = re.compile(r"!\[(.*?)\]\((?!http)(.*?)\)")
    content = relative_image_regex.sub(
        lambda m: f"![{m.group(1)}]({get_resource_url(repo, branch, base_path / m.group(2))})",
        content,
    )
    return content


def handle_post(  # pylint: disable=too-many-arguments
    file_path: Path,
    base_path: Path,
    repo: str,
    branch: str,
    publication_id: str,
    headers: Dict[str, str],
    results: Dict[str, List[Dict[str, str]]],
    added_files: List[Path],
) -> None:
    """Handle a markdown post file."""
    metadata, content = process_markdown(file_path)
    validate_frontmatter(metadata)

    content = update_image_urls(content, base_path, repo, branch)

    if "coverImage" in metadata and not metadata["coverImage"].startswith("http"):
        metadata["coverImage"] = get_resource_url(repo, branch, base_path / metadata["coverImage"])

    metadata["contentMarkdown"] = content
    metadata["publicationId"] = publication_id

    post_data = {
        "title": metadata["title"],
        "subtitle": metadata.get("subtitle"),
        "publicationId": publication_id,
        "contentMarkdown": metadata["contentMarkdown"],
        "publishedAt": metadata["publishedAt"],
        "coverImageOptions": {
            "coverImageURL": metadata.get("coverImage"),
            "coverImageAttribution": metadata.get("coverImageAttribution"),
        },
        "slug": metadata["slug"],
        "tags": metadata["tags"],
        "settings": {"enableTableOfContent": metadata.get("enableTableOfContents", False), "slugOverridden": True},
    }

    post_id = get_post_id(publication_id, metadata["slug"], headers)
    if post_id:
        post_data["id"] = post_id
    post = create_or_update_post(post_data, headers)
    results["added" if file_path in added_files else "modified"].append(post)


def handle_deleted_post(
    file_path: Path, publication_id: str, headers: Dict[str, str], results: Dict[str, List[Dict[str, str]]]
) -> None:
    """Handle a deleted markdown post file."""
    metadata, _ = process_markdown(file_path)
    validate_frontmatter(metadata)
    post_id = get_post_id(publication_id, metadata["slug"], headers)
    if post_id:
        success = delete_post(post_id, headers)
        if success:
            results["deleted"].append({"slug": metadata["slug"]})


def write_results_to_github_output(results: Dict[str, List[Dict[str, str]]]) -> None:
    """Write the results to the GitHub output in two different formats."""
    github_output_path = os.getenv("GITHUB_OUTPUT")
    with open(github_output_path, "a", encoding="utf-8") as f:
        f.write(f"result_json={json.dumps(results)}\n")
        f.write(f"result_summary={json.dumps(results, indent=2)}\n")


def main():
    """Main entrypoint for the action."""
    access_token = os.environ["ACCESS_TOKEN"]
    posts_directory = Path(os.environ.get("POSTS_DIRECTORY", ""))
    publication_host = os.environ["PUBLICATION_HOST"]

    changed_files = json.loads(os.environ["CHANGED_FILES"])
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ["GITHUB_REF"].split("/")[-1]
    added_files = [Path(f) for f in changed_files.get("added_files", [])]
    modified_files = [Path(f) for f in changed_files.get("modified_files", [])]
    deleted_files = [Path(f) for f in changed_files.get("deleted_files", [])]

    headers = {"Authorization": f"Bearer {access_token}"}
    publication_id = get_publication_id(publication_host, headers)

    results = {"added": [], "modified": [], "deleted": []}

    for file_path in added_files + modified_files:
        if file_path.is_relative_to(posts_directory) and file_path.suffix == ".md":
            handle_post(file_path, file_path.parent, repo, branch, publication_id, headers, results, added_files)

    for file_path in deleted_files:
        if file_path.is_relative_to(posts_directory) and file_path.suffix == ".md":
            handle_deleted_post(file_path, publication_id, headers, results)

    write_results_to_github_output(results)


if __name__ == "__main__":
    main()
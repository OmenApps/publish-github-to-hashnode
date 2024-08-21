"""Provides a class to manage the publication of markdown posts to a Hashnode publication."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from zoneinfo import ZoneInfo

import requests

from constants import HASHNODE_API_URL, HEADERS, PUBLICATION_HOST


class HashnodeAPI:
    """Manage the publication of markdown posts to a Hashnode publication."""

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the HashnodeAPI class with a timeout and obtain the publication ID."""
        self.timeout = timeout
        self.debug_data: List[List[Union[datetime, str]]] = []
        self.publication_id = self._fetch_publication_id()

    def _fetch_publication_id(self) -> str:
        """Fetch the publication ID for the given host."""
        query = """
        query Publication($host: String!) {
            publication(host: $host) {
                id
            }
        }
        """
        response = self._execute_request(query, variables={"host": PUBLICATION_HOST})
        publication_id = response["data"]["publication"]["id"]
        self.debug_data.append(
            [datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S"), f"Publication ID: {publication_id}"]
        )
        return publication_id

    def get_post_id(self, slug: str) -> Optional[str]:
        """Get the post ID for the given publication and slug."""
        query = """
        query GetPost($host: String!, $slug: String!) {
            publication(host: $host) {
                post(slug: $slug) {
                    id
                }
            }
        }
        """
        response = self._execute_request(query, variables={"host": PUBLICATION_HOST, "slug": slug})
        post = response["data"]["publication"].get("post")
        post_id = post["id"] if post else None
        self.debug_data.append(
            [
                datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
                f"Slug: {slug}, Post ID: {post_id}, Post: {post if post else None}",
            ]
        )
        return post_id

    def get_all_publication_posts(self) -> List[Dict[str, str]]:
        """Get a list of all post IDs and slugs for a publication."""
        query = """
        query GetPosts($host: String!, $first: Int!, $after: String) {
            publication(host: $host) {
                posts(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            slug
                        }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
        """
        all_posts = []
        variables = {"host": PUBLICATION_HOST, "first": 50, "after": None}
        while True:
            response = self._execute_request(query, variables=variables)
            posts_data = response["data"]["publication"]["posts"]
            all_posts.extend({"id": edge["node"]["id"], "slug": edge["node"]["slug"]} for edge in posts_data["edges"])
            if not posts_data["pageInfo"]["hasNextPage"]:
                break
            variables["after"] = posts_data["pageInfo"]["endCursor"]

        return all_posts

    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, str]:
        """Create a post with the given data."""
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
        response = self._execute_request(mutation, variables={"input": post_data})
        return self._extract_post_data(response, "Created Post", post_data)

    def update_post(self, post_data: Dict[str, Any]) -> Dict[str, str]:
        """Update a post with the given data."""
        mutation = """
        mutation UpdatePost($input: UpdatePostInput!) {
            updatePost(input: $input) {
                post {
                    id
                    title
                    slug
                }
            }
        }
        """
        response = self._execute_request(mutation, variables={"input": post_data})
        return self._extract_post_data(response, "Updated Post", post_data)

    def delist_post(self, post_id: str) -> bool:
        """Delist (soft-delete) the post with the given ID."""
        mutation = """
        mutation UpdatePost($input: UpdatePostInput!) {
            updatePost(input: $input) {
                post {
                    id
                    settings {
                        delisted
                    }
                }
            }
        }
        """
        post_data = {"id": post_id, "settings": {"delisted": True}}
        response = self._execute_request(mutation, variables={"input": post_data})

        try:
            delisted = response["data"]["updatePost"]["post"]["settings"]["delisted"]
            self.debug_data.append([datetime.now(ZoneInfo("UTC")), f"Delisted post: {post_id}, Delisted: {delisted}"])
            return delisted
        except KeyError:
            self._log_failure("Failed to delist post", post_id, response)
            return False

    def _execute_request(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL request and return the JSON response."""
        response = requests.post(
            url=HASHNODE_API_URL,
            json={"query": query, "variables": variables},
            headers=HEADERS,
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.debug_data.append(
                [
                    datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
                    f"Request failed with status code {response.status_code}: {response.text}. "
                    f"{query=}, {variables=}. Original exception: {e}.",
                ]
            )
            return {}
        return response.json()

    def _extract_post_data(self, response: Dict[str, Any], action: str, post_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract post data from the response and handle errors."""
        try:
            post = response["data"][f"{action.split()[0].lower()}Post"]["post"]
            self.debug_data.append(
                [
                    datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
                    f"{action}: {post['id']}, {post['title']}, {post['slug']}",
                ]
            )
            return post
        except KeyError:
            self._log_failure(f"Failed to {action.lower()}", post_data, response)
            return {}

    def _log_failure(self, message: str, identifier: str, response: Dict[str, Any]) -> None:
        """Log a failure with a given message, identifier, and response."""
        self.debug_data.append(
            [
                datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
                f"{message} with identifier: {identifier}. Response: {response}",
            ]
        )

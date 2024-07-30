"""
Provides a class to manage the publication of markdown posts to a Hashnode publication.
"""

from typing import Any, Dict, List, Optional

import requests

from constants import HASHNODE_API_URL, HEADERS, PUBLICATION_HOST


class HashnodeAPI:
    """Manage the publication of markdown posts to a Hashnode publication."""

    def __init__(
        self,
        timeout: int = 30,
    ):
        """Initialize the HashnodeAPI class."""
        self.timeout = timeout
        self.debug_data = []
        self.publication_id = self._get_publication_id()

    def _get_publication_id(self) -> str:
        """Get the publication ID for the given host."""
        query = """
        query Publication($host: String!) {
            publication(host: $host) {
                id
            }
        }
        """
        response = requests.post(
            url=HASHNODE_API_URL,
            json={"query": query, "variables": {"host": PUBLICATION_HOST}},
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        publication_id = response.json()["data"]["publication"]["id"]
        self.debug_data.append(f"Publication ID: {publication_id}")
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
        response = requests.post(
            url=HASHNODE_API_URL,
            json={
                "query": query,
                "variables": {"host": PUBLICATION_HOST, "slug": slug},
            },
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        post = response.json()["data"]["publication"]["post"]
        post_id = post["id"] if post else None
        self.debug_data.append(f"Slug: {slug}, Post ID: {post_id}, Post: {post}")
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
        variables = {
            "host": PUBLICATION_HOST,
            "first": 50,
            "after": None,
        }

        all_posts = []
        has_next_page = True
        while has_next_page:
            response = requests.post(
                url=HASHNODE_API_URL,
                json={"query": query, "variables": variables},
                headers=HEADERS,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()["data"]["publication"]["posts"]
            all_posts.extend([{"id": edge["node"]["id"], "slug": edge["node"]["slug"]} for edge in data["edges"]])
            has_next_page = data["pageInfo"]["hasNextPage"]
            variables["after"] = data["pageInfo"]["endCursor"]

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
        response = requests.post(
            url=HASHNODE_API_URL,
            json={"query": mutation, "variables": {"input": post_data}},
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        response_json = response.json()["data"]["publishPost"]["post"]
        self.debug_data.append(f"Created Post - Data: {post_data}, Post: {response_json}")
        return response_json

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
        response = requests.post(
            url=HASHNODE_API_URL,
            json={"query": mutation, "variables": {"input": post_data}},
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        response_json = response.json()["data"]["updatePost"]["post"]
        self.debug_data.append(f"Updated Post - Data: {post_data}, Post: {response_json}")
        return response_json

    def delist_post(self, post_id: str) -> bool:
        """Update the post settings to delist the post with the given ID."""
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
        response = requests.post(
            url=HASHNODE_API_URL,
            json={"query": mutation, "variables": {"input": post_data}},
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        response_json = response.json()["data"]["updatePost"]["post"]
        self.debug_data.append(f"Delisted Post - ID: {post_id}, Post: {response_json}")
        return response_json["settings"]["delisted"]

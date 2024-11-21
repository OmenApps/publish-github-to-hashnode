"""Provides a class to manage the publication of markdown posts to a Hashnode publication.

This is intended to be used with the `sgqlc` and schema.py, but we are trying a different implementation.

Remove this file once we confirm the new implementation works as expected.
"""

# import logging
# from datetime import datetime
# from typing import Any, Optional
# from zoneinfo import ZoneInfo

# import requests
# from constants import (  # Was removed for new implementation
#     HASHNODE_API_URL,
#     HEADERS,
#     PUBLICATION_HOST,
# )
# from sgqlc.operation import Operation

# from .schema import (
#     Mutation,
#     Post,
#     Publication,
#     PublishPostInput,
#     Query,
#     RemovePostInput,
#     UpdatePostInput,
#     schema,
# )

# logger = logging.getLogger(__name__)


# class HashnodeAPI:
#     """Manage the publication of markdown posts to a Hashnode publication."""

#     def __init__(self, timeout: int = 30) -> None:
#         """Initialize the HashnodeAPI class with a timeout and obtain the publication ID."""
#         self.timeout = timeout
#         self.debug_data: list[list[datetime | str]] = []
#         self.publication_id = self._fetch_publication_id()

#     def _fetch_publication_id(self) -> str:
#         """Fetch the publication ID for the given host."""
#         op = Operation(Query)
#         publication = op.publication(host=PUBLICATION_HOST)
#         publication.id()

#         response = self._execute_request(op)
#         publication_id = response["publication"]["id"]
#         self.debug_data.append(
#             [datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"), f"Publication ID: {publication_id}"]
#         )
#         return publication_id

#     def get_post_id(self, slug: str) -> Optional[str]:
#         """Get the post ID for the given publication and slug."""
#         op = Operation(Query)
#         publication = op.publication(host=PUBLICATION_HOST)
#         post = publication.post(slug=slug)
#         post.id()

#         response = self._execute_request(op)

#         if "errors" in response:
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"GraphQL errors: {response['errors']}, Slug: {slug}",
#                 ]
#             )
#             return None

#         post_data = response["publication"].get("post")
#         post_id = post_data["id"] if post_data else None
#         self.debug_data.append(
#             [
#                 datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                 f"Got post id {post_id} for {slug}, Post: {post_data if post_data else None}",
#             ]
#         )
#         return post_id

#     def get_all_publication_posts(self) -> list[dict[str, str]]:
#         """Get a list of all post IDs and slugs for a publication."""
#         all_posts = []
#         has_next_page = True
#         after_cursor = None

#         while has_next_page:
#             op = Operation(Query)
#             publication = op.publication(host=PUBLICATION_HOST)
#             posts = publication.posts(first=50, after=after_cursor)

#             # Select fields from edges
#             post_edges = posts.edges()
#             node = post_edges.node()
#             node.id()
#             node.slug()

#             # Get pagination info
#             page_info = posts.page_info()
#             page_info.has_next_page()
#             page_info.end_cursor()

#             response = self._execute_request(op)
#             posts_data = response["publication"]["posts"]

#             all_posts.extend({"id": edge["node"]["id"], "slug": edge["node"]["slug"]} for edge in posts_data["edges"])

#             has_next_page = posts_data["pageInfo"]["hasNextPage"]
#             after_cursor = posts_data["pageInfo"]["endCursor"] if has_next_page else None

#         return all_posts

#     def create_post(self, post_data: dict[str, Any]) -> dict[str, str]:
#         """Create a post with the given data."""
#         op = Operation(Mutation)
#         publish_post = op.publish_post(input=post_data)
#         post = publish_post.post()
#         post.id()
#         post.title()
#         post.slug()

#         response = self._execute_request(op)
#         return self._extract_post_data(response, "Create Post", post_data)

#     def update_post(self, post_data: dict[str, Any]) -> dict[str, str]:
#         """Update a post with the given data."""
#         op = Operation(Mutation)
#         update_post = op.update_post(input=post_data)
#         post = update_post.post()
#         post.id()
#         post.title()
#         post.slug()

#         response = self._execute_request(op)
#         return self._extract_post_data(response, "Update Post", post_data)

#     def delist_post(self, post_id: str) -> bool:
#         """Delist (soft-delete) the post with the given ID."""
#         op = Operation(Mutation)
#         update_post = op.update_post(input={"id": post_id, "preferences": {"isDelisted": True}})
#         post = update_post.post()
#         post.id()
#         preferences = post.preferences()
#         preferences.is_delisted()

#         response = self._execute_request(op)

#         try:
#             delisted = response["updatePost"]["post"]["preferences"]["isDelisted"]
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"Delisted post: {post_id}, Delisted: {delisted}",
#                 ]
#             )
#             return delisted
#         except KeyError:
#             self._log_failure("Failed to delist post", post_id, response)
#             return False

#     def _execute_request(self, operation: Operation) -> dict[str, Any]:
#         """Execute a GraphQL request and return the JSON response."""
#         try:
#             response = requests.post(
#                 url=HASHNODE_API_URL,
#                 json={"query": str(operation), "variables": operation.variables},
#                 headers=HEADERS,
#                 timeout=self.timeout,
#             )
#             response.raise_for_status()
#             result = response.json()

#             if "data" in result:
#                 return result["data"]
#             return result

#         except requests.exceptions.HTTPError as e:
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"Request failed with status code {response.status_code}: {response.text}. "
#                     f"Query: {str(operation)}, Variables: {operation.variables}. Original exception: {e}.",
#                 ]
#             )
#             return {}
#         except requests.exceptions.RequestException as e:
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"Request failed with {response.text=}: {e}. Query: {str(operation)}, "
#                     f"Variables: {operation.variables}.",
#                 ]
#             )
#             return {}
#         except Exception as e:  # pylint: disable=W0718
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"Unexpected error {getattr(response, 'text', '')}: {e}. "
#                     f"Query: {str(operation)}, Variables: {operation.variables}.",
#                 ]
#             )
#             return {}

#     def _extract_post_data(self, response: dict[str, Any], action: str, post_data: dict[str, Any]) -> dict[str, str]:
#         """Extract post data from the response and handle errors."""
#         try:
#             self.debug_data.append(
#                 [
#                     datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                     f"{action.split()[0].lower()=}",
#                 ]
#             )
#             post = response[f"{action.split()[0].lower()}Post"]["post"]

#             if post:
#                 self.debug_data.append(
#                     [
#                         datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                         f"{action}: {post['id']=}, {post['title']=}, {post['slug']=}",
#                     ]
#                 )
#             else:
#                 self._log_failure(f"Failed to {action.lower()} (No Post was returned in response)", post_data, response)

#             return post
#         except KeyError:
#             self._log_failure(f"Failed to {action.lower()}", post_data, response)
#             return {}

#     def _log_failure(self, message: str, identifier: str, response: dict[str, Any]) -> None:
#         """Log a failure with a given message, identifier, and response."""
#         self.debug_data.append(
#             [
#                 datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S:%f"),
#                 f"{message}. {response=}. Tried using identifier: {identifier}.",
#             ]
#         )

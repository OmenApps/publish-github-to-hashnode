"""Service for managing blog posts."""
from pathlib import Path
from typing import Any, Optional

from sgqlc.operation import Operation

from .exceptions import PublicationError
from .graphql_client import GraphQLClient
from .markdown_processor import MarkdownProcessor
from .models import Post
from .schema import Mutation, Query


class PostService:
    """Service for managing blog posts."""

    def __init__(
        self,
        graphql_client: GraphQLClient,
        markdown_processor: MarkdownProcessor,
        settings: Any,
    ):
        self.graphql_client = graphql_client
        self.markdown_processor = markdown_processor
        self.settings = settings

    def publish_post(self, file_path: Path) -> dict[str, Any]:
        """Publish or update a post from a markdown file."""
        post = self.markdown_processor.process_file(file_path)
        post_id = self.get_post_id(post.slug)

        post_data = self._build_post_data(post, post_id)
        return self._publish_or_update(post_data, post_id)

    def get_post_id(self, slug: str) -> Optional[str]:
        """Get the ID of an existing post by slug."""
        op = Operation(Query)
        publication = op.publication(host=self.settings.PUBLICATION_HOST)
        post = publication.post(slug=slug)
        post.id()

        response = self.graphql_client.execute(op)
        post_data = response.get("publication", {}).get("post")
        return post_data["id"] if post_data else None

    def _build_post_data(self, post: Post, post_id: Optional[str] = None) -> dict[str, Any]:
        """Build the post data for the API."""
        data = {
            "title": post.metadata.title,
            "subtitle": post.metadata.subtitle,
            "publicationId": post.publication_id,
            "contentMarkdown": post.content,
            "tags": post.metadata.tags,
            "publishedAt": post.metadata.publishedAt,
            "slug": post.slug,
            "coverImageOptions": {
                "coverImageURL": post.metadata.coverImage,
                "coverImageAttribution": post.metadata.coverImageAttribution,
            },
        }

        if post_id:
            data["id"] = post_id
            data["settings"] = {
                "isTableOfContentEnabled": post.metadata.enableTableOfContents,
                "delisted": post.metadata.delisted,
                "disableComments": post.metadata.disableComments,
            }
        else:
            data["settings"] = {
                "enableTableOfContent": post.metadata.enableTableOfContents,
                "delisted": post.metadata.delisted,
                "slugOverridden": True,
            }
            data["disableComments"] = post.metadata.disableComments

        return data

    def _publish_or_update(self, post_data: dict[str, Any], post_id: Optional[str]) -> dict[str, Any]:
        """Publish a new post or update an existing one."""
        op = Operation(Mutation)

        if post_id:
            mutation = op.update_post(input=post_data)
        else:
            mutation = op.publish_post(input=post_data)

        post = mutation.post()
        post.id()
        post.title()
        post.slug()

        response = self.graphql_client.execute(op)
        operation_name = "updatePost" if post_id else "publishPost"

        if operation_name not in response:
            raise PublicationError(f"Failed to {operation_name.split('_', maxsplit=1)[0]} post")

        return response[operation_name]["post"]

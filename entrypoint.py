"""Main application module for publishing posts to Hashnode."""
import json
import logging
import uuid
from pathlib import Path

from sgqlc.operation import Operation

from schema import Query
from src.exceptions import HashnodePublisherError
from src.graphql_client import GraphQLClient
from src.markdown_processor import MarkdownProcessor
from src.post_service import PostService
from src.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HashnodePublisher:
    """Main application class for publishing posts to Hashnode."""

    def __init__(self):
        self.graphql_client = GraphQLClient(
            url=settings.HASHNODE_API_URL,
            headers=settings.headers,
        )

        self.markdown_processor = MarkdownProcessor(
            publication_id=self._get_publication_id(),
            github_raw_url=settings.GITHUB_RAW_URL,
            repository=settings.GITHUB_REPOSITORY,
            branch=settings.branch,
        )

        self.settings = settings

        self.post_service = PostService(
            graphql_client=self.graphql_client,
            markdown_processor=self.markdown_processor,
            settings=self.settings,
        )

        self.results = {"added": [], "modified": [], "deleted": [], "errors": [], "debug_data": []}

    def _get_publication_id(self) -> str:
        """Get the publication ID for the given host."""
        op = Operation(Query)
        publication = op.publication(host=settings.PUBLICATION_HOST)
        publication.id()

        response = self.graphql_client.execute(op)
        return response["publication"]["id"]

    def process_files(self):
        """Process all changed files."""
        for file_path in settings.ADDED_FILES + settings.CHANGED_FILES:
            if not self._is_valid_post_file(file_path):
                self.results["errors"].append(
                    {"file": str(file_path), "error": "Not a markdown file in the posts directory"}
                )
                continue

            try:
                is_new = file_path in settings.ADDED_FILES
                result = self.post_service.publish_post(file_path)
                self.results["added" if is_new else "modified"].append(result)
                logger.info("Successfully %s post: %s", "added" if is_new else "modified", result["title"])

            except HashnodePublisherError as e:
                self.results["errors"].append({"file": str(file_path), "error": str(e)})
                logger.error("Error processing %s: %s", file_path, e)

    def _is_valid_post_file(self, file_path: Path) -> bool:
        """Check if the file is a markdown file in the posts directory."""
        return file_path.suffix.lower() == ".md" and file_path.is_relative_to(settings.POSTS_DIRECTORY)

    def write_results(self):
        """Write results to GitHub Actions output."""
        if not settings.GITHUB_OUTPUT:
            logger.warning("GITHUB_OUTPUT not set, skipping results output")
            return

        # Add debug data from clients
        self.results["debug_data"] = self.graphql_client.debug_data

        with open(settings.GITHUB_OUTPUT, "a", encoding="utf-8") as f:
            # Write JSON results
            print(f"result_json={json.dumps(self.results)}", file=f)

            # Write text summary
            delimiter = str(uuid.uuid4())
            print(f"result_summary<<{delimiter}", file=f)
            print(self._create_summary(), file=f)
            print(delimiter, file=f)

    def _create_summary(self) -> str:
        """Create a human-readable summary of the results."""
        summary = []

        # Add results for each category
        for category in ["added", "modified", "deleted"]:
            if self.results[category]:
                summary.append(f"{category.capitalize()} posts:")
                for post in self.results[category]:
                    summary.append(f"  - {post['title']} ({post['slug']})")
            else:
                summary.append(f"No {category} posts.")

        # Add errors if any
        if self.results["errors"]:
            summary.append("\nErrors:")
            for error in self.results["errors"]:
                summary.append(f"  - {error['file']}: {error['error']}")

        # Add debug data if any
        if self.results["debug_data"]:
            summary.append("\nDebug Data:")
            for timestamp, message in self.results["debug_data"]:
                summary.append(f"  - [{timestamp}] {message}")

        return "\n".join(summary)


def main():
    """Main entry point for the application."""
    try:
        publisher = HashnodePublisher()
        publisher.process_files()
        publisher.write_results()

    except HashnodePublisherError as e:
        logger.error("Fatal error: %s", e)
        exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred: %s", e)
        exit(1)


if __name__ == "__main__":
    main()

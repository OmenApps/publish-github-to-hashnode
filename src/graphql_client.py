"""GraphQL client for making API requests."""
from typing import Any

import requests
from sgqlc.operation import Operation

from .exceptions import APIError


class GraphQLClient:
    """GraphQL client for making API requests."""

    def __init__(self, url: str, headers: dict[str, str], timeout: int = 30):
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.debug_data: list[tuple[str, str]] = []

    def execute(self, operation: Operation) -> dict[str, Any]:
        """Execute a GraphQL operation."""
        try:
            response = requests.post(
                url=self.url,
                json={"query": str(operation), "variables": operation.variables},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()

            if "errors" in result:
                raise APIError(f"GraphQL errors: {result['errors']}")

            if "data" in result:
                return result["data"]
            return result

        except requests.exceptions.RequestException as e:
            self.debug_data.append(("error", f"GraphQL request failed: {str(e)}"))
            raise APIError(f"GraphQL request failed: {str(e)}") from e

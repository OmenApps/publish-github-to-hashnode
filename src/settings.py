"""Application settings using Pydantic for validation."""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic for validation."""

    ACCESS_TOKEN: str
    POSTS_DIRECTORY: Path = Path("")
    PUBLICATION_HOST: str
    GITHUB_REPOSITORY: str
    GITHUB_REF: str
    GITHUB_OUTPUT: str | None = None

    ADDED_FILES: list[Path] = []
    CHANGED_FILES: list[Path] = []

    HASHNODE_API_URL: str = "https://gql.hashnode.com"
    GITHUB_RAW_URL: str = "https://raw.githubusercontent.com"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"

    @property
    def headers(self) -> dict[str, str]:
        """Get API headers with authorization."""
        return {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}

    @property
    def branch(self) -> str:
        """Get Git branch name."""
        return self.GITHUB_REF.split("/")[-1]


settings = Settings()

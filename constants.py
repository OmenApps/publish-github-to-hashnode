"""
This file contains the constants used in the application.

ACCESS_TOKEN, POSTS_DIRECTORY, PUBLICATION_HOST, GITHUB_REPOSITORY, and BRANCH are read from the environment variables.

- POSTS_DIRECTORY is the directory where the markdown posts are stored.
- PUBLICATION_HOST is the host of the Hashnode publication where the posts will be published.
- GITHUB_REPOSITORY is the name of the GitHub repository where the action is triggered.
- BRANCH is the branch or tag ref that triggered the action.
- ACCESS_TOKEN is used to authenticate the requests to the Hashnode API.
- HEADERS constant is a dictionary that contains the Authorization header with the ACCESS_TOKEN.
- GITHUB_RAW_URL is the base URL for the raw content of the GitHub repository.
- HASHNODE_API_URL is the URL of the Hashnode GraphQL API.
- ADDED_FILES and CHANGED_FILES are the paths of the added and changed files in the Git commit.
- ALL_CHANGED_FILES is the list of all changed files (added and changed).
"""

import os
from pathlib import Path

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
POSTS_DIRECTORY = Path(os.environ.get("POSTS_DIRECTORY", ""))
PUBLICATION_HOST = os.environ["PUBLICATION_HOST"]
GITHUB_OUTPUT = os.getenv("GITHUB_OUTPUT")

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ["GITHUB_REF"].split("/")[-1]

HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

GITHUB_RAW_URL = "https://raw.githubusercontent.com"
HASHNODE_API_URL = "https://gql.hashnode.com"

added_files = os.environ.get("ADDED_FILES", "").split()
ADDED_FILES = [Path(f) for f in added_files if f]

changed_files = os.environ.get("CHANGED_FILES", "").split()
CHANGED_FILES = [Path(f) for f in changed_files if f and f not in added_files]

ALL_CHANGED_FILES = list(set(ADDED_FILES + CHANGED_FILES))

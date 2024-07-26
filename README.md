# Publish GitHub to Hashnode GitHub Action

This GitHub Action publishes blog posts from a GitHub repository to a specific publication on Hashnode. It reads markdown files, processes the frontmatter and content, and uses the Hashnode API to create, update, or delete posts.

## Features

- Create new posts on Hashnode if they do not exist.
- Update existing posts on Hashnode if they exist.
- Delete posts on Hashnode if the corresponding markdown file is deleted.
- Handles correct linking of cover images and inline images in the markdown content.

## Inputs

- `access-token` (required): Your Hashnode API Personal Access Token. See: [Hashnode Developer Settings](https://hashnode.com/settings/developer)
- `changed-files` (required): The list of changed files in the repository, provided by the `tj-actions/changed-files` action.
- `publication-host` (required): The publication host (e.g., `blog.mydomain.com`).
- `posts-directory` (optional): The local directory containing the blog posts, if different from the root directory. Default: `posts`

## Outputs

- `result_json`: Publish result as a JSON string.
- `result_summary`: Publish result summary formatted as text.

## Usage

### 1. Create a `.github/workflows/publish.yml` file

Create a new workflow file in your repository to define the steps required to publish the posts.

```yaml
name: Publish My Hashnode Blog Posts
on:
  push:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0

        - name: Get changed files
          id: changed-files
          uses: tj-actions/changed-files@v44

        - uses: actions/setup-python@v5
          with:
            python-version: '3.x'

        - name: Publish to Hashnode
          uses: actions/publish-github-to-hashnode@v1
          with:
            access-token: ${{ secrets.HASHNODE_ACCESS_TOKEN }}
            changed-files: ${{ steps.changed-files.outputs.all_changed_files }}
            publication-host: 'blog.mydomain.com'  # Your publication host
            posts-directory: 'content/posts'  # The directory within your repository containing the markdown files, if different from the root directory
```

### 2. Store your Hashnode API Access Token as a GitHub Secret

1. Obtain your Hashnode API Personal Access Token. See: [Hashnode Developer Settings](https://hashnode.com/settings/developer)
2. Go to your repository on GitHub.
3. Click on `Settings`.
4. Scroll down to `Secrets and variables` and click on `Actions`.
5. Click `New repository secret`.
6. Add a new secret with the name `HASHNODE_ACCESS_TOKEN` and your Hashnode API token as the value.

### 3. Prepare your repository structure

Ensure your repository contains the markdown files you wish to publish in the specified directory (default is the root of the repository).

### 4. Markdown Post Frontmatter

#### Frontmatter Fields

Full list of frontmatter fields that can be used in the markdown files:

- `title` (required): Title of the post.
- `subtitle` (optional): Subtitle of the post.
- `slug` (required): Slug of the post.
- `tags` (optional): Tags of the post (comma-separated).
- `enableTableOfContents` (optional, default: false): Enable table of contents.
- `publish` (optional, default: true): Should the post be published at this time.
- `coverImage` (optional): Cover image relative path within the repository starting from `posts-directory` (as specified in pubish.yml) if provided.
- `coverImageAttribution`: Information about the cover image attribution (optional)
- `publishedAt`: Date and time when the post was published (optional)

#### Example Frontmatter

```markdown
---
title: Creating Spaghetti in Docker Compose
slug: creating-spaghetti-in-docker-compose
tags: docker,docker-compose
enableTableOfContents: true
coverImage: images/cover.jpg
---

## Introduction

This is an introduction to creating spaghetti in Docker Compose.

## Ingredients

- Docker Engine
- Spaghetti
- Sauce
- Cheese
- Love

## Steps

1. ...
2. ...
3. ...
```

### 5. Handling Image URLs

The action will automatically convert relative image URLs to absolute URLs that point to the raw content on GitHub. Ensure your image paths in the markdown are correct relative paths.

## Example Workflow Using `result_json`

You can utilize the `result_json` output in subsequent steps to get the result of the publish operation in json format. The approach below can also be used with `result_summary` for a text summary.

```yaml
name: Publish My Hashnode Blog Posts
on:
  push:

jobs:
    publish:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0

        - name: Get changed files
          id: changed-files
          uses: tj-actions/changed-files@v44
        
        - uses: actions/setup-python@v5
          with:
            python-version: '3.x'
                
        - name: Publish to Hashnode
          id: publish
          uses: actions/publish-github-to-hashnode@v1
          with:
            access-token: ${{ secrets.HASHNODE_ACCESS_TOKEN }}
            changed-files: ${{ steps.changed-files.outputs.all_changed_files }}
            publication-host: 'blog.mydomain.com'
            posts-directory: 'content/posts'
        
        - name: Get the output JSON
          run: echo "${{ steps.publish.outputs.result_json }}"
```

## Development

To contribute to the development of this action, clone the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Questions and Support

If you have any questions or need support, please open an issue in the GitHub repository. I will do my best to help.

"""Custom exceptions for the Hashnode Publisher."""


class HashnodePublisherError(Exception):
    """Base exception for the application."""

    pass


class InvalidPostError(HashnodePublisherError):
    """Raised when a post is invalid."""

    pass


class APIError(HashnodePublisherError):
    """Raised when an API request fails."""

    pass


class ConfigurationError(HashnodePublisherError):
    """Raised when there's a configuration error."""

    pass


class PublicationError(HashnodePublisherError):
    """Raised when there's an error with the publication."""

    pass

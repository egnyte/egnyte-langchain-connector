"""
Filename: exceptions.py
Application: Egnyte  LangChain Retriever
Copyright: Copyright (c) 2025 Egnyte Inc.

Exception classes for the LangChain Retriever API SDK.

This module defines custom exception classes for the SDK client library.
These exceptions provide specific error handling for different types of
API failures, network issues, and validation errors.

Classes:
    LangChainAPIError: Base exception for API-related errors
    LangChainConnectionError: Network connection errors
    LangChainTimeoutError: Request timeout errors
    LangChainValidationError: Request validation errors
    LangChainAuthenticationError: Authentication failures

Functions:
    None
"""

from typing import Any, Dict, Optional


class LangChainAPIError(Exception):
    """Base exception for LangChain API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(LangChainAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(LangChainAPIError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, status_code=403)


class NotFoundError(LangChainAPIError):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(LangChainAPIError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str = "Request validation failed",
        errors: Optional[list] = None,
    ):
        super().__init__(message, status_code=422)
        self.errors = errors or []


class RateLimitError(LangChainAPIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ServerError(LangChainAPIError):
    """Raised when server encounters an error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)


class TimeoutError(LangChainAPIError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message)


class ConnectionError(LangChainAPIError):
    """Raised when connection to API fails."""

    def __init__(self, message: str = "Failed to connect to API"):
        super().__init__(message)

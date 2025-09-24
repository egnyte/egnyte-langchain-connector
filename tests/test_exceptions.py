"""Tests for custom exception classes."""

import pytest

from langchain_egnyte.exceptions import (
    AuthenticationError,
    ConnectionError,
    LangChainAPIError,
    NotFoundError,
    ValidationError,
)


class TestLangChainAPIError:
    """Test cases for LangChainAPIError base exception."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        error = LangChainAPIError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_data == {}

    def test_initialization_with_status_code(self):
        """Test exception initialization with status code."""
        error = LangChainAPIError("Test error", status_code=500)

        assert str(error) == "[500] Test error"
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.response_data == {}

    def test_initialization_with_response_data(self):
        """Test exception initialization with response data."""
        response_data = {"error": "Server error", "details": "Internal error"}
        error = LangChainAPIError("Test error", response_data=response_data)

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response_data == response_data

    def test_initialization_with_all_parameters(self):
        """Test exception initialization with all parameters."""
        response_data = {"error": "Bad request", "code": "INVALID_PARAM"}
        error = LangChainAPIError(
            "Complete error", status_code=400, response_data=response_data
        )

        assert str(error) == "[400] Complete error"
        assert error.message == "Complete error"
        assert error.status_code == 400
        assert error.response_data == response_data

    def test_repr(self):
        """Test string representation."""
        error = LangChainAPIError("Test error", status_code=500)
        repr_str = repr(error)

        # The repr should contain the class name and the error message
        assert "LangChainAPIError" in repr_str
        assert "Test error" in repr_str


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    def test_default_status_code(self):
        """Test that AuthenticationError has default status code 401."""
        error = AuthenticationError("Invalid token")

        assert error.status_code == 401
        assert str(error) == "[401] Invalid token"
        assert error.message == "Invalid token"

    def test_default_message(self):
        """Test that AuthenticationError has default message."""
        error = AuthenticationError()

        assert error.status_code == 401
        assert str(error) == "[401] Authentication failed"
        assert error.message == "Authentication failed"

    def test_with_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Token expired")

        assert error.status_code == 401
        assert str(error) == "[401] Token expired"
        assert error.message == "Token expired"

    def test_inheritance(self):
        """Test that AuthenticationError inherits from LangChainAPIError."""
        error = AuthenticationError("Auth error")

        assert isinstance(error, LangChainAPIError)
        assert isinstance(error, AuthenticationError)


class TestValidationError:
    """Test cases for ValidationError."""

    def test_default_status_code(self):
        """Test that ValidationError has default status code 422."""
        error = ValidationError("Invalid parameters")

        assert error.status_code == 422
        assert str(error) == "[422] Invalid parameters"
        assert error.message == "Invalid parameters"
        assert error.errors == []

    def test_with_errors_list(self):
        """Test ValidationError with errors list."""
        errors_list = ["Field 'query' is required", "Field 'limit' must be positive"]
        error = ValidationError("Validation failed", errors=errors_list)

        assert error.status_code == 422
        assert str(error) == "[422] Validation failed"
        assert error.message == "Validation failed"
        assert error.errors == errors_list

    def test_inheritance(self):
        """Test that ValidationError inherits from LangChainAPIError."""
        error = ValidationError("Validation error")

        assert isinstance(error, LangChainAPIError)
        assert isinstance(error, ValidationError)


class TestNotFoundError:
    """Test cases for NotFoundError."""

    def test_default_status_code(self):
        """Test that NotFoundError has default status code 404."""
        error = NotFoundError("Resource not found")

        assert error.status_code == 404
        assert str(error) == "[404] Resource not found"
        assert error.message == "Resource not found"

    def test_default_message(self):
        """Test NotFoundError with default message."""
        error = NotFoundError()

        assert error.status_code == 404
        assert str(error) == "[404] Resource not found"
        assert error.message == "Resource not found"

    def test_inheritance(self):
        """Test that NotFoundError inherits from LangChainAPIError."""
        error = NotFoundError("Not found error")

        assert isinstance(error, LangChainAPIError)
        assert isinstance(error, NotFoundError)


class TestConnectionError:
    """Test cases for ConnectionError."""

    def test_basic_initialization(self):
        """Test basic ConnectionError initialization."""
        error = ConnectionError("Connection failed")

        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
        assert error.status_code is None  # Network errors don't have HTTP status codes

    def test_with_custom_message(self):
        """Test ConnectionError with custom message."""
        error = ConnectionError("Connection timeout")

        assert str(error) == "Connection timeout"
        assert error.message == "Connection timeout"
        assert error.status_code is None
        assert error.response_data == {}

    def test_default_message(self):
        """Test ConnectionError with default message."""
        error = ConnectionError()

        assert str(error) == "Failed to connect to API"
        assert error.message == "Failed to connect to API"
        assert error.status_code is None

    def test_inheritance(self):
        """Test that ConnectionError inherits from LangChainAPIError."""
        error = ConnectionError("Network error")

        assert isinstance(error, LangChainAPIError)
        assert isinstance(error, ConnectionError)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and relationships."""

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from LangChainAPIError."""
        exceptions = [
            AuthenticationError("test"),
            ValidationError("test"),
            NotFoundError("test"),
            ConnectionError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, LangChainAPIError)

    def test_exception_catching(self):
        """Test that specific exceptions can be caught by base class."""

        def raise_auth_error():
            raise AuthenticationError("Auth failed")

        def raise_validation_error():
            raise ValidationError("Validation failed")

        # Test catching specific exception
        with pytest.raises(AuthenticationError):
            raise_auth_error()

        # Test catching by base class
        with pytest.raises(LangChainAPIError):
            raise_auth_error()

        with pytest.raises(LangChainAPIError):
            raise_validation_error()

    def test_exception_types_are_distinct(self):
        """Test that different exception types are distinct."""
        auth_error = AuthenticationError("Auth error")
        validation_error = ValidationError("Validation error")

        assert type(auth_error) is not type(validation_error)
        assert not isinstance(auth_error, ValidationError)
        assert not isinstance(validation_error, AuthenticationError)

    def test_status_code_defaults(self):
        """Test that each exception type has correct default status code."""
        assert AuthenticationError("test").status_code == 401
        assert ValidationError("test").status_code == 422
        assert NotFoundError("test").status_code == 404
        assert ConnectionError("test").status_code is None
        assert LangChainAPIError("test").status_code is None


class TestExceptionUsagePatterns:
    """Test cases for common exception usage patterns."""

    def test_exception_with_context(self):
        """Test exception with additional context information."""
        errors_list = ["Query is required", "Invalid base_url format"]

        error = ValidationError("Query validation failed", errors=errors_list)

        assert error.errors == errors_list
        assert "Query is required" in error.errors

    def test_exception_chaining(self):
        """Test exception chaining with underlying causes."""
        try:
            # Simulate an underlying exception
            raise ConnectionError("Network unreachable")
        except ConnectionError as e:
            # Chain with our custom exception
            network_error = ConnectionError(f"Failed to connect: {e}")
            network_error.__cause__ = e

            assert network_error.__cause__ is e
            assert "Network unreachable" in str(network_error)

    def test_exception_serialization(self):
        """Test that exceptions can be serialized for logging."""
        errors_list = ["test_error", "another_error"]
        error = ValidationError("Test error", errors=errors_list)

        # Test that all attributes are accessible
        error_dict = {
            "message": error.message,
            "status_code": error.status_code,
            "response_data": error.response_data,
            "errors": error.errors,
            "type": type(error).__name__,
        }

        assert error_dict["message"] == "Test error"
        assert error_dict["status_code"] == 422
        assert error_dict["response_data"] == {}
        assert error_dict["errors"] == errors_list
        assert error_dict["type"] == "ValidationError"

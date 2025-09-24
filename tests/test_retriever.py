"""Tests for EgnyteRetriever class."""

from unittest.mock import Mock, patch

import pytest
from langchain_core.documents import Document

from langchain_egnyte import EgnyteRetriever, EgnyteSearchOptions
from langchain_egnyte.exceptions import (
    AuthenticationError,
    LangChainAPIError,
    ValidationError,
)


class TestEgnyteRetriever:
    """Test cases for EgnyteRetriever."""

    def setup_method(self):
        """Set up test fixtures."""
        self.domain = "test.egnyte.com"
        self.base_url = "https://test.egnyte.com"  # Expected base URL
        self.retriever = EgnyteRetriever(domain=self.domain)

    def test_init_with_domain(self):
        """Test retriever initialization with domain."""
        assert self.retriever.domain == self.domain
        assert self.retriever.base_url == self.base_url
        assert self.retriever.search_options is None  # Default when not provided

    def test_init_with_search_options(self):
        """Test retriever initialization with custom search options."""
        search_options = EgnyteSearchOptions(limit=50, folderPath="/test")
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)
        assert retriever.search_options.limit == 50
        assert retriever.search_options.folderPath == "/test"

    def test_query_validation_in_api_request(self):
        """Test query validation in API request."""
        # Test empty query
        with pytest.raises(ValidationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("", "test_token")
        assert "query must be 1-1000 characters" in str(exc_info.value)

    def test_query_validation_whitespace(self):
        """Test query validation with whitespace-only input."""
        with pytest.raises(ValidationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("   ", "test_token")
        assert "query must be 1-1000 characters" in str(exc_info.value)

    def test_query_validation_too_long(self):
        """Test query validation with too long input."""
        long_query = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth(long_query, "test_token")
        assert "query must be 1-1000 characters" in str(exc_info.value)

    def test_token_validation(self):
        """Test token validation."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("test query", "")
        assert "egnyte_user_token is required" in str(exc_info.value)

    @patch("langchain_egnyte.retriever.httpx.Client.post")
    def test_get_relevant_documents_success(self, mock_post):
        """Test successful document retrieval."""
        # Mock response with correct structure
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "documents": [
                {
                    "content": "Test document content",
                    "metadata": {
                        "source": "egnyte",
                        "title": "test_document.pdf",
                        "file_path": "/Shared/test_document.pdf",
                        "entry_id": "123",
                        "score": 0.95,
                        "size": 1024,
                        "content_type": "application/pdf",
                    },
                }
            ]
        }
        mock_post.return_value = mock_response

        # Test retrieval
        token = "test_token"
        documents = self.retriever.get_relevant_documents_with_auth("test query", token)

        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].page_content == "Test document content"
        assert documents[0].metadata["title"] == "test_document.pdf"
        assert documents[0].metadata["file_path"] == "/Shared/test_document.pdf"
        assert documents[0].metadata["size"] == 1024

    @patch("langchain_egnyte.retriever.httpx.Client.post")
    def test_get_relevant_documents_authentication_error(self, mock_post):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"x-request-id": "auth-error-123"}
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth(
                "test query", "invalid_token"
            )

        assert exc_info.value.status_code == 401
        assert "auth-error-123" in str(exc_info.value)  # Check request ID is included

    @patch("langchain_egnyte.retriever.httpx.Client")
    def test_get_relevant_documents_validation_error(self, mock_client):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "error": "Validation failed",
            "details": ["Invalid query parameter"],
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        with pytest.raises(ValidationError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("", "valid_token")

        assert exc_info.value.status_code == 422

    @patch("langchain_egnyte.retriever.httpx.Client.post")
    def test_get_relevant_documents_not_found_error(self, mock_post):
        """Test not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {"x-request-id": "not-found-123"}
        mock_response.json.return_value = {"error": "Resource not found"}
        mock_post.return_value = mock_response

        # 404 falls into the "unexpected status code" category
        with pytest.raises(LangChainAPIError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("test query", "valid_token")

        assert "404" in str(exc_info.value)
        assert "not-found-123" in str(exc_info.value)

    @patch("langchain_egnyte.retriever.httpx.Client.post")
    def test_get_relevant_documents_network_error(self, mock_post):
        """Test network error handling."""
        import httpx

        mock_post.side_effect = httpx.ConnectError("Connection failed")

        # Network errors are wrapped in LangChainAPIError
        with pytest.raises(LangChainAPIError) as exc_info:
            self.retriever.get_relevant_documents_with_auth("test query", "valid_token")

        assert "Failed to connect to API" in str(exc_info.value)

    def test_retriever_properties(self):
        """Test retriever properties and configuration."""
        assert self.retriever.base_url == self.base_url
        assert self.retriever.search_options is None  # No default search options

    def test_retriever_with_custom_search_options(self):
        """Test retriever with custom search options."""
        search_options = EgnyteSearchOptions(
            limit=25, folderPath="/test", collectionId="123"
        )
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)

        assert retriever.search_options.limit == 25
        assert retriever.search_options.folderPath == "/test"
        assert retriever.search_options.collectionId == "123"

    @pytest.mark.asyncio
    async def test_async_invoke(self):
        """Test async document retrieval via ainvoke."""
        # Mock the async API request method directly
        with patch.object(self.retriever, "_amake_api_request") as mock_api:
            mock_api.return_value = {
                "documents": [
                    {
                        "content": "async test content",
                        "metadata": {"source": "egnyte", "title": "async_test.pdf"},
                    }
                ]
            }

            # Test async method
            documents = await self.retriever.ainvoke(
                "test query", egnyte_user_token="test_token"
            )

            assert len(documents) == 1
            assert documents[0].page_content == "async test content"
            assert documents[0].metadata["title"] == "async_test.pdf"

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.retriever)
        assert "EgnyteRetriever" in repr_str
        assert self.domain in repr_str

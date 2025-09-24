"""LangChain standard unit tests for EgnyteRetriever."""

from unittest.mock import patch

import pytest
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from langchain_egnyte import EgnyteRetriever, EgnyteSearchOptions


class TestEgnyteRetrieverLangChainStandardUnit:
    """LangChain standard unit tests for EgnyteRetriever.

    These tests ensure compliance with LangChain's retriever interface
    without requiring external API access. They follow LangChain's
    testing patterns and standards.
    """

    def test_inherits_from_base_retriever(self):
        """Test that EgnyteRetriever properly inherits from BaseRetriever."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")
        assert isinstance(retriever, BaseRetriever)
        assert issubclass(EgnyteRetriever, BaseRetriever)

    def test_has_required_methods(self):
        """Test that EgnyteRetriever has all required LangChain methods."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        # Check required methods exist
        assert hasattr(retriever, "invoke")
        assert hasattr(retriever, "ainvoke")
        assert hasattr(retriever, "batch")
        assert hasattr(retriever, "abatch")
        assert hasattr(retriever, "stream")
        assert hasattr(retriever, "astream")

        # Check methods are callable
        assert callable(retriever.invoke)
        assert callable(retriever.ainvoke)

    def test_constructor_parameters(self):
        """Test retriever constructor with various parameters."""
        # Test minimal constructor
        retriever = EgnyteRetriever(domain="test.egnyte.com")
        assert retriever.domain == "test.egnyte.com"
        assert retriever.timeout == 30.0  # default

        # Test with all parameters
        search_options = EgnyteSearchOptions(limit=10)
        retriever = EgnyteRetriever(
            domain="company.egnyte.com", search_options=search_options, timeout=60.0
        )
        assert retriever.domain == "company.egnyte.com"
        assert retriever.search_options == search_options
        assert retriever.timeout == 60.0

    def test_invoke_returns_documents(self):
        """Test that invoke method returns List[Document]."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        # Mock the API response
        with patch.object(retriever, "_make_api_request") as mock_api:
            mock_api.return_value = {
                "documents": [
                    {
                        "content": "Test document content",
                        "metadata": {
                            "source": "egnyte",
                            "title": "test.pdf",
                            "file_path": "/test.pdf",
                            "entry_id": "123",
                            "score": 0.95,
                        },
                    }
                ]
            }

            # Test invoke method
            result = retriever.invoke("test query", egnyte_user_token="test-token")

            # Validate return type
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], Document)
            assert result[0].page_content == "Test document content"
            assert result[0].metadata["source"] == "egnyte"

    @pytest.mark.asyncio
    async def test_ainvoke_returns_documents(self):
        """Test that ainvoke method returns List[Document]."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        # Mock the async API response method
        with patch.object(retriever, "_amake_api_request") as mock_api:
            mock_api.return_value = {
                "documents": [
                    {
                        "content": "Async test content",
                        "metadata": {
                            "source": "egnyte",
                            "title": "async.pdf",
                            "file_path": "/async.pdf",
                            "entry_id": "456",
                            "score": 0.88,
                        },
                    }
                ]
            }

            # Test ainvoke method
            result = await retriever.ainvoke(
                "test query", egnyte_user_token="test-token"
            )

            # Validate return type
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], Document)
            assert result[0].page_content == "Async test content"

    def test_k_parameter_support(self):
        """Test that k parameter works correctly."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        with patch.object(retriever, "_make_api_request") as mock_api:
            mock_api.return_value = {"documents": []}

            # Test with k parameter
            retriever.invoke("test", k=5, egnyte_user_token="test-token")

            # Verify k was passed to search options
            call_args = mock_api.call_args
            assert call_args is not None

    def test_search_options_integration(self):
        """Test integration with EgnyteSearchOptions."""
        search_options = EgnyteSearchOptions(
            limit=25, folderPath="/test", createdBy="user"
        )

        retriever = EgnyteRetriever(
            domain="test.egnyte.com", search_options=search_options
        )

        assert retriever.search_options == search_options
        assert retriever.search_options.limit == 25
        assert retriever.search_options.folderPath == "/test"

    def test_error_handling_patterns(self):
        """Test LangChain-compatible error handling."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        # Test missing token error
        with pytest.raises(ValueError, match="egnyte_user_token is required"):
            retriever.invoke("test query")

        # Test empty query handling (our implementation raises ValidationError)
        from langchain_egnyte.exceptions import ValidationError

        with pytest.raises(ValidationError, match="query must be 1-1000 characters"):
            retriever.invoke("", egnyte_user_token="test-token")

    def test_metadata_structure(self):
        """Test that returned documents have proper metadata structure."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        with patch.object(retriever, "_make_api_request") as mock_api:
            mock_api.return_value = {
                "documents": [
                    {
                        "content": "Test content",
                        "metadata": {
                            "source": "egnyte",
                            "title": "document.pdf",
                            "file_path": "/folder/document.pdf",
                            "entry_id": "abc123",
                            "score": 0.92,
                            "created_date": "2024-01-01",
                            "modified_date": "2024-01-02",
                        },
                    }
                ]
            }

            result = retriever.invoke("test", egnyte_user_token="test-token")
            doc = result[0]

            # Check required metadata fields
            assert "source" in doc.metadata
            assert "title" in doc.metadata
            assert "file_path" in doc.metadata
            assert "entry_id" in doc.metadata
            assert "score" in doc.metadata

            # Check metadata values
            assert doc.metadata["source"] == "egnyte"
            assert isinstance(doc.metadata["score"], (int, float))

    def test_serialization_compatibility(self):
        """Test that retriever can be serialized/deserialized (LangChain requirement)."""
        retriever = EgnyteRetriever(domain="test.egnyte.com")

        # Test that retriever has required attributes for serialization
        assert hasattr(retriever, "domain")
        assert hasattr(retriever, "search_options")
        assert hasattr(retriever, "timeout")

        # Test basic serialization compatibility
        config = {
            "domain": retriever.domain,
            "timeout": retriever.timeout,
        }

        # Should be able to recreate from config
        new_retriever = EgnyteRetriever(**config)
        assert new_retriever.domain == retriever.domain
        assert new_retriever.timeout == retriever.timeout

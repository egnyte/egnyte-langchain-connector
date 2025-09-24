"""Live integration tests for EgnyteRetriever with real API calls."""

import pytest
from langchain_core.documents import Document

from langchain_egnyte import EgnyteRetriever, EgnyteSearchOptions
from langchain_egnyte.exceptions import AuthenticationError, LangChainAPIError


def handle_api_errors(func, *args, **kwargs):
    """Helper function to handle common API errors with retry logic."""
    import time

    max_retries = 3
    base_delay = 5

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # Add exponential backoff delay for retries
                delay = base_delay * (2 ** (attempt - 1))
                print(
                    f"Retrying after {delay} seconds (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(delay)

            return func(*args, **kwargs)

        except LangChainAPIError as e:
            if "429" in str(e) or "Rate limit" in str(e):
                if attempt < max_retries - 1:
                    # Will retry with delay
                    continue
                else:
                    # Final attempt failed, skip the test
                    pytest.skip(
                        "Rate limit exceeded after retries - this is expected behavior during testing"
                    )
            elif "403" in str(e):
                pytest.skip("Access forbidden - may be due to token permissions")
            else:
                raise  # Re-raise if it's a different error


@pytest.mark.integration
class TestEgnyteRetrieverLiveIntegration:
    """Live integration tests that make actual API calls to Egnyte."""

    def test_basic_search_with_credentials(self, egnyte_credentials):
        """Test basic search functionality with real credentials."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        # Perform a basic search
        results = handle_api_errors(
            retriever.invoke, "test", egnyte_user_token=egnyte_credentials["user_token"]
        )

        # Verify results structure
        assert isinstance(results, list)
        for doc in results:
            assert isinstance(doc, Document)
            assert hasattr(doc, "page_content")
            assert hasattr(doc, "metadata")
            assert "source" in doc.metadata
            assert doc.metadata["source"] == "egnyte"

    def test_search_with_options(self, egnyte_credentials):
        """Test search with custom search options."""
        search_options = EgnyteSearchOptions(limit=5, folderPath="/Shared")

        retriever = EgnyteRetriever(
            domain=egnyte_credentials["domain"], search_options=search_options
        )

        results = handle_api_errors(
            retriever.invoke,
            "document",
            egnyte_user_token=egnyte_credentials["user_token"],
        )

        # Should return at most 5 results due to limit
        assert len(results) <= 5
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_async_search(self, egnyte_credentials):
        """Test async search functionality."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        async def async_invoke():
            return await retriever.ainvoke(
                "test", egnyte_user_token=egnyte_credentials["user_token"]
            )

        try:
            results = await async_invoke()

            assert isinstance(results, list)
            for doc in results:
                assert isinstance(doc, Document)

        except LangChainAPIError as e:
            # Handle rate limiting and access errors gracefully
            if "429" in str(e) or "Rate limit" in str(e):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            elif "403" in str(e):
                pytest.skip(
                    "Access forbidden - may be due to token permissions or rate limiting"
                )
            else:
                raise  # Re-raise if it's a different error

    def test_empty_query_handling(self, egnyte_credentials):
        """Test handling of empty or minimal queries."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        # Test with minimal query - expect API to return 400 for very short queries
        try:
            retriever.invoke("a", egnyte_user_token=egnyte_credentials["user_token"])
            # If no exception, that's also fine - some APIs might accept single character queries

        except LangChainAPIError as e:
            # Handle expected errors and rate limiting
            if "400" in str(e):
                # Expected behavior for minimal queries
                pass
            elif "403" in str(e):
                # Access forbidden - may be due to token permissions
                pytest.skip(
                    "Access forbidden - may be due to token permissions or API restrictions"
                )
            elif "429" in str(e) or "Rate limit" in str(e):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            else:
                raise  # Re-raise if it's a different error

    def test_invalid_token_error(self, egnyte_credentials):
        """Test error handling with invalid token."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        with pytest.raises((AuthenticationError, LangChainAPIError)):
            retriever.invoke("test", egnyte_user_token="invalid_token_12345")

    def test_domain_validation(self):
        """Test domain validation in retriever initialization."""
        # Valid domain
        retriever = EgnyteRetriever(domain="valid.egnyte.com")
        assert retriever.domain == "valid.egnyte.com"
        assert retriever.base_url == "https://valid.egnyte.com"

    def test_search_options_validation(self, egnyte_credentials):
        """Test search options validation."""
        # Test with various search options
        search_options = EgnyteSearchOptions(
            limit=10,
            folderPath="/Shared",
            createdAfter=1640995200000,  # 2022-01-01 timestamp in milliseconds
        )

        retriever = EgnyteRetriever(
            domain=egnyte_credentials["domain"], search_options=search_options
        )

        results = handle_api_errors(
            retriever.invoke,
            "document",
            egnyte_user_token=egnyte_credentials["user_token"],
        )

        assert isinstance(results, list)

    def test_timeout_configuration(self, egnyte_credentials):
        """Test timeout configuration."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"], timeout=60.0)

        assert retriever.timeout == 60.0

        # Should work with longer timeout
        results = handle_api_errors(
            retriever.invoke, "test", egnyte_user_token=egnyte_credentials["user_token"]
        )

        assert isinstance(results, list)

    def test_metadata_completeness(self, egnyte_credentials):
        """Test that returned documents have complete metadata."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        results = handle_api_errors(
            retriever.invoke, "test", egnyte_user_token=egnyte_credentials["user_token"]
        )

        if results:  # If we have results
            doc = results[0]

            # Check required metadata fields
            assert "source" in doc.metadata
            assert doc.metadata["source"] == "egnyte"

            # Check for common metadata fields (may vary by document)
            expected_fields = ["title", "file_path", "entry_id"]
            for field in expected_fields:
                if field in doc.metadata:
                    assert doc.metadata[field] is not None

    def test_batch_processing(self, egnyte_credentials):
        """Test batch processing of multiple queries."""
        retriever = EgnyteRetriever(domain=egnyte_credentials["domain"])

        queries = ["test", "document", "file"]

        # Process queries individually (batch method would need implementation)
        results = []
        for query in queries:
            result = handle_api_errors(
                retriever.invoke,
                query,
                egnyte_user_token=egnyte_credentials["user_token"],
            )
            results.append(result)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)

    def test_large_result_handling(self, egnyte_credentials):
        """Test handling of potentially large result sets."""
        search_options = EgnyteSearchOptions(limit=50)  # Request more results

        retriever = EgnyteRetriever(
            domain=egnyte_credentials["domain"], search_options=search_options
        )

        results = handle_api_errors(
            retriever.invoke, "test", egnyte_user_token=egnyte_credentials["user_token"]
        )

        # Should handle large result sets gracefully
        assert isinstance(results, list)
        assert len(results) <= 50  # Respects limit

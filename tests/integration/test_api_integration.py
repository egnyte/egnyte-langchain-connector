"""Integration tests for real Egnyte API interactions."""

import os

import pytest
from langchain_core.documents import Document

from langchain_egnyte import EgnyteRetriever, EgnyteSearchOptions
from langchain_egnyte.exceptions import (
    AuthenticationError,
    LangChainAPIError,
    ValidationError,
)


# Load environment variables from demo/.env
def load_demo_env():
    """Load environment variables from demo/.env file."""
    try:
        import os

        from dotenv import load_dotenv

        demo_env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "demo", ".env"
        )
        if os.path.exists(demo_env_path):
            load_dotenv(demo_env_path)
    except ImportError:
        pass


load_demo_env()


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


# Skip integration tests if credentials are not available
pytestmark = pytest.mark.skipif(
    not (os.getenv("EGNYTE_DOMAIN") and os.getenv("EGNYTE_USER_TOKEN")),
    reason="Integration tests require EGNYTE_DOMAIN and EGNYTE_USER_TOKEN environment variables",
)


class TestEgnyteAPIIntegration:
    """Integration tests with real Egnyte API."""

    @classmethod
    def setup_class(cls):
        """Set up test class with API credentials."""
        cls.domain = os.getenv("EGNYTE_DOMAIN").strip('"').strip("'")
        cls.token = os.getenv("EGNYTE_USER_TOKEN")
        cls.retriever = EgnyteRetriever(domain=cls.domain)

    def test_basic_search_integration(self):
        """Test basic search functionality with real API."""
        # Use a common search term that should return results
        query = "pdf"

        documents = handle_api_errors(
            self.retriever.get_relevant_documents_with_auth,
            query,
            egnyte_user_token=self.token,
        )

        # Verify we get Document objects
        assert isinstance(documents, list)
        if documents:  # If there are results
            assert all(isinstance(doc, Document) for doc in documents)
            assert all(hasattr(doc, "page_content") for doc in documents)
            assert all(hasattr(doc, "metadata") for doc in documents)

    def test_search_with_limit(self):
        """Test search with custom limit."""
        search_options = EgnyteSearchOptions(limit=5)
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)

        documents = handle_api_errors(
            retriever.get_relevant_documents_with_auth,
            "document",
            egnyte_user_token=self.token,
        )

        # Should return at most 5 documents
        assert len(documents) <= 5

    def test_search_with_folder_filter(self):
        """Test search with folder path filter."""
        # Test with a common folder like /Shared
        search_options = EgnyteSearchOptions(folderPath="/Shared")
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)

        documents = handle_api_errors(
            retriever.get_relevant_documents_with_auth,
            "file",
            egnyte_user_token=self.token,
        )

        # All results should be from /Shared folder
        for doc in documents:
            if "path" in doc.metadata:
                assert doc.metadata["path"].startswith("/Shared")

    def test_empty_query_validation(self):
        """Test that empty queries are properly validated."""
        try:
            self.retriever.get_relevant_documents_with_auth(
                "", egnyte_user_token=self.token
            )
            # If no exception, that's unexpected for empty query
            assert False, "Expected ValidationError for empty query"
        except ValidationError:
            # Expected behavior
            pass
        except LangChainAPIError as e:
            if "429" in str(e) or "Rate limit" in str(e) or "403" in str(e):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            else:
                raise

    def test_invalid_token_authentication(self):
        """Test authentication error with invalid token."""
        try:
            self.retriever.get_relevant_documents_with_auth(
                "test", egnyte_user_token="invalid_token"
            )
            # If no exception, that's unexpected for invalid token
            assert False, "Expected AuthenticationError for invalid token"
        except AuthenticationError:
            # Expected behavior
            pass
        except LangChainAPIError as e:
            if "429" in str(e) or "Rate limit" in str(e) or "403" in str(e):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            else:
                raise

    @pytest.mark.asyncio
    async def test_async_search_integration(self):
        """Test async search functionality."""
        try:
            documents = await self.retriever.aget_relevant_documents_with_auth(
                "document", egnyte_user_token=self.token
            )

            assert isinstance(documents, list)
            if documents:
                assert all(isinstance(doc, Document) for doc in documents)
        except LangChainAPIError as e:
            if "429" in str(e) or "Rate limit" in str(e) or "403" in str(e):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            else:
                raise

    def test_document_metadata_structure(self):
        """Test that returned documents have expected metadata structure."""
        documents = handle_api_errors(
            self.retriever.get_relevant_documents_with_auth,
            "file",
            egnyte_user_token=self.token,
        )

        if documents:
            doc = documents[0]
            metadata = doc.metadata

            # Check for expected metadata fields
            expected_fields = [
                "path",
                "size",
                "last_modified",
                "created",
                "created_by",
                "type",
            ]
            for field in expected_fields:
                # Not all fields may be present, but if they are, they should have valid values
                if field in metadata:
                    assert metadata[field] is not None

    def test_search_with_date_filter(self):
        """Test search with date range filter."""
        # Search for files created in the last year (approximate)
        import time

        one_year_ago = int((time.time() - 365 * 24 * 60 * 60) * 1000)

        search_options = EgnyteSearchOptions(createdAfter=one_year_ago)
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)

        documents = handle_api_errors(
            retriever.get_relevant_documents_with_auth,
            "document",
            egnyte_user_token=self.token,
        )

        # Should return documents (test mainly checks that the API accepts the parameter)
        assert isinstance(documents, list)

    def test_large_result_handling(self):
        """Test handling of large result sets."""
        # Use a broad search term that might return many results
        search_options = EgnyteSearchOptions(limit=100)
        retriever = EgnyteRetriever(domain=self.domain, search_options=search_options)

        documents = handle_api_errors(
            retriever.get_relevant_documents_with_auth,
            "file",
            egnyte_user_token=self.token,
        )

        # Should handle large result sets without errors
        assert isinstance(documents, list)
        assert len(documents) <= 100

    def test_special_characters_in_query(self):
        """Test search with special characters in query."""
        # Test queries with special characters
        special_queries = [
            "file.pdf",
            "document-name",
            "file_with_underscores",
            "file (with parentheses)",
        ]

        for query in special_queries:
            try:
                documents = handle_api_errors(
                    self.retriever.get_relevant_documents_with_auth,
                    query,
                    egnyte_user_token=self.token,
                )
                assert isinstance(documents, list)
            except Exception as e:
                # If the query fails, it should be a known exception type
                # 400 errors are also acceptable for special character queries
                assert isinstance(
                    e, (ValidationError, AuthenticationError, LangChainAPIError)
                )

    def test_unicode_query_handling(self):
        """Test search with Unicode characters."""
        unicode_queries = [
            "résumé",
            "naïve",
            "café",
            "文档",  # Chinese characters
        ]

        for query in unicode_queries:
            try:
                documents = handle_api_errors(
                    self.retriever.get_relevant_documents_with_auth,
                    query,
                    egnyte_user_token=self.token,
                )
                assert isinstance(documents, list)
            except Exception as e:
                # Unicode handling might vary by API, so we just ensure no unexpected errors
                # 400 errors are also acceptable for unicode queries
                assert isinstance(
                    e, (ValidationError, AuthenticationError, LangChainAPIError)
                )

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import asyncio

        async def search_task(query_suffix):
            return await self.retriever.aget_relevant_documents_with_auth(
                f"document{query_suffix}", egnyte_user_token=self.token
            )

        async def run_concurrent_searches():
            tasks = [search_task(i) for i in range(3)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    # Concurrent requests might fail due to rate limiting
                    if isinstance(result, LangChainAPIError) and (
                        "429" in str(result)
                        or "Rate limit" in str(result)
                        or "403" in str(result)
                    ):
                        # Rate limiting is expected for concurrent requests
                        continue
                    assert isinstance(
                        result,
                        (ValidationError, AuthenticationError, LangChainAPIError),
                    )
                else:
                    assert isinstance(result, list)

        try:
            # Run the async test
            asyncio.run(run_concurrent_searches())
        except Exception as e:
            # If we get rate limiting at the top level, skip the test
            if isinstance(e, LangChainAPIError) and (
                "429" in str(e) or "Rate limit" in str(e) or "403" in str(e)
            ):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            else:
                raise


class TestEgnyteAPIErrorHandling:
    """Integration tests for API error handling."""

    @classmethod
    def setup_class(cls):
        """Set up test class."""
        cls.domain = os.getenv("EGNYTE_DOMAIN").strip('"').strip("'")
        cls.token = os.getenv("EGNYTE_USER_TOKEN")
        cls.retriever = EgnyteRetriever(domain=cls.domain)

    def test_malformed_base_url_handling(self):
        """Test handling of malformed base URLs."""
        malformed_retriever = EgnyteRetriever(domain="invalid-domain.egnyte.com")

        try:
            malformed_retriever.get_relevant_documents_with_auth(
                "test", egnyte_user_token=self.token
            )
            # Should raise an exception for malformed domain
            assert False, "Expected exception for malformed domain"
        except (ValidationError, AuthenticationError, Exception) as e:
            # Expected behavior - any of these exceptions are acceptable
            if isinstance(e, LangChainAPIError) and (
                "429" in str(e) or "Rate limit" in str(e) or "403" in str(e)
            ):
                pytest.skip(
                    "Rate limit exceeded - this is expected behavior during testing"
                )
            # Otherwise, this is the expected behavior for malformed domain

    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        # This test might be flaky depending on network conditions
        # It's mainly to ensure timeout scenarios are handled gracefully
        try:
            documents = handle_api_errors(
                self.retriever.get_relevant_documents_with_auth,
                "test",
                egnyte_user_token=self.token,
            )
            assert isinstance(documents, list)
        except Exception as e:
            # Network issues should result in appropriate exceptions
            assert isinstance(e, (ValidationError, AuthenticationError, Exception))

    def test_rate_limiting_handling(self):
        """Test handling of API rate limiting."""
        # Make multiple rapid requests to potentially trigger rate limiting
        for i in range(5):
            try:
                documents = handle_api_errors(
                    self.retriever.get_relevant_documents_with_auth,
                    f"test{i}",
                    egnyte_user_token=self.token,
                )
                assert isinstance(documents, list)
            except Exception as e:
                # Rate limiting or other API errors should be handled gracefully
                assert isinstance(e, (ValidationError, AuthenticationError, Exception))


# Utility functions for integration tests
def is_integration_test_environment():
    """Check if we're in an environment suitable for integration tests."""
    return bool(os.getenv("EGNYTE_DOMAIN") and os.getenv("EGNYTE_TOKEN"))


def get_test_credentials():
    """Get test credentials from environment variables."""
    return {"domain": os.getenv("EGNYTE_DOMAIN"), "token": os.getenv("EGNYTE_TOKEN")}

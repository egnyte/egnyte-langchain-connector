"""
Filename: retriever.py
Application: Egnyte LangChain Retriever
Copyright: Copyright (c) 2025 Egnyte Inc.

LangChain-compatible retriever for Egnyte documents.

This module provides a LangChain-compatible retriever class that follows
the same pattern as other LangChain retrievers.
It integrates with Egnyte's Hybrid search API while providing the standard
LangChain retriever interface.

Classes:
    EgnyteRetriever: LangChain-compatible retriever class
    EgnyteSearchOptions: Configuration options for search

Usage:
    from egnyte_retriever import EgnyteRetriever

    retriever = EgnyteRetriever(domain="company.egnyte.com")
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

try:
    from langchain_core.callbacks.manager import (
        AsyncCallbackManagerForRetrieverRun,
        CallbackManagerForRetrieverRun,
    )
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever
except ImportError as e:
    raise ImportError(
        "LangChain is required for this SDK. Please install it with:\n"
        "pip install langchain-core>=0.1.0\n"
        "or\n"
        "pip install langchain>=0.1.0\n"
        "\nFor specific AI provider integrations, also install:\n"
        "pip install langchain-openai>=0.1.0  # For OpenAI\n"
        "pip install langchain-anthropic>=0.1.0  # For Anthropic\n"
        "pip install langchain-azure-openai>=0.1.0  # For Azure OpenAI\n"
        f"\nOriginal error: {e}"
    )

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    LangChainAPIError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from .utilities import EgnyteSearchOptions

# Module-level logger
logger = logging.getLogger(__name__)


class EgnyteRetriever(BaseRetriever):
    """
    LangChain-compatible retriever for Egnyte documents.

    This retriever provides a LangChain-compatible interface for searching
    and retrieving documents from Egnyte using our API.

    Features:
        - Configurable HTTP request timeout (default: 30.0 seconds)
        - Flexible search options and filtering
        - Token-per-request authentication model
        - Comprehensive error handling with timeout detection

    Example:
        Basic usage with default timeout:
        >>> retriever = EgnyteRetriever(domain="company.egnyte.com")

        Custom timeout configuration:
        >>> retriever = EgnyteRetriever(
        ...     domain="company.egnyte.com",
        ...     timeout=60.0  # 60 seconds for slower networks
        ... )
    """

    domain: str
    search_options: Optional[EgnyteSearchOptions] = None
    timeout: float = 30.0
    k: int = 100  # Number of documents to return (LangChain standard)

    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
    }

    def __init__(
        self,
        domain: str,
        search_options: Optional[EgnyteSearchOptions] = None,
        timeout: float = 30.0,
        k: int = 100,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the EgnyteRetriever.

        Args:
            domain: Egnyte domain (e.g., "company.egnyte.com" or
                "https://company.egnyte.com")
            search_options: Default search options for all queries
                (optional)
            timeout: HTTP request timeout in seconds
                (default: 30.0)
            k: Number of documents to return
                (default: 100, LangChain standard)
            **kwargs: Additional arguments passed to BaseRetriever

        Note:
            User tokens are provided per search request, not stored in
            the retriever.
            Search options can be provided per request for maximum
            flexibility.
        """
        # Initialize BaseRetriever with all arguments
        super().__init__(  # type: ignore[call-arg]
            domain=domain, search_options=search_options, timeout=timeout, k=k, **kwargs
        )

        # Construct base URL from domain (not a Pydantic field)
        self._base_url = self._construct_base_url(self.domain)

        # HTTP client for API calls
        self._http_client = httpx.Client(timeout=self.timeout)

    def _construct_base_url(self, domain: str) -> str:
        """
        Construct the base URL from the domain.

        Args:
            domain: Egnyte domain (with or without https://)

        Returns:
            Properly formatted base URL

        Examples:
            "company.egnyte.com" -> "https://company.egnyte.com"
            "https://company.egnyte.com" -> "https://company.egnyte.com"
            "https://company.egnyte.com/" -> "https://company.egnyte.com"
        """
        domain = domain.strip()

        if not domain:
            raise ValueError("Domain cannot be empty")

        # Remove trailing slash if present
        domain = domain.rstrip("/")

        # Ensure https:// protocol (replace http:// if present)
        if domain.startswith("http://"):
            domain = domain.replace("http://", "https://", 1)
        elif not domain.startswith("https://"):
            domain = f"https://{domain}"

        # Validate that it looks like an Egnyte domain
        if ".egnyte.com" not in domain:
            raise ValueError(
                f"Invalid Egnyte domain: {domain}. "
                "Domain should be in format 'company.egnyte.com' or "
                "'https://company.egnyte.com'"
            )

        return domain

    @property
    def base_url(self) -> str:
        """Get the constructed base URL."""
        return self._base_url

    def _extract_request_id(self, response: httpx.Response) -> Optional[str]:
        """
        Extract Egnyte request ID from response headers for troubleshooting.

        Args:
            response: HTTP response object

        Returns:
            Request ID string if found, None otherwise

        Note:
            Request IDs are useful for troubleshooting errors with Egnyte support.
        """
        # Common header names that might contain the request ID
        request_id_headers = [
            "x-egnyte-request-id",  # Egnyte-specific
            "x-request-id",  # Common standard
            "request-id",  # Alternative standard
            "x-correlation-id",  # Correlation tracking
            "x-trace-id",  # Trace tracking
            "x-amzn-requestid",  # AWS-based services
            "x-amzn-trace-id",  # AWS X-Ray
        ]

        for header_name in request_id_headers:
            request_id = response.headers.get(header_name)
            if request_id:
                return str(request_id)

        return None

    def _validate_request_inputs(self, query: str, egnyte_user_token: str) -> None:
        """
        Validate inputs for API requests.

        Args:
            query: The search query string
            egnyte_user_token: The Egnyte user authentication token

        Raises:
            ValidationError: When query is empty or too long
            AuthenticationError: When token is missing
        """
        if not query or len(query.strip()) == 0:
            raise ValidationError("query must be 1-1000 characters")
        if len(query) > 1000:
            raise ValidationError("query must be 1-1000 characters")
        if not egnyte_user_token:
            raise AuthenticationError("egnyte_user_token is required")

    def _get_request_data(
        self, query: str, egnyte_user_token: str, search_options: EgnyteSearchOptions
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        """
        Prepare request data and headers for API calls.

        Args:
            query: The search query string
            egnyte_user_token: The Egnyte user authentication token
            search_options: Search configuration options

        Returns:
            Tuple of (request_data, headers) dictionaries
        """
        # Prepare base request data with query
        request_data: Dict[str, Any] = {"query": query.strip()}

        # Add search options (exclude_unset=True only includes explicitly set values)
        search_data = search_options.model_dump(exclude_unset=True)
        request_data.update(search_data)
        # Force pure keyword search (semanticWeight=0.0)
        request_data["semanticWeight"] = 0.0

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {egnyte_user_token}",
            "Content-Type": "application/json",
        }

        return request_data, headers

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and convert to appropriate exceptions.

        Args:
            response: The HTTP response object from httpx

        Returns:
            Dictionary containing the JSON response data

        Raises:
            AuthenticationError: For 401 status codes
            ValidationError: For 422 status codes
            RateLimitError: For 429 status codes
            ServerError: For 5xx status codes
            LangChainAPIError: For other unexpected status codes
        """
        if response.status_code == 200:
            json_data = response.json()
            return json_data if isinstance(json_data, dict) else {}

        # Extract request ID for troubleshooting
        request_id = self._extract_request_id(response)
        request_id_info = f" (Request ID: {request_id})" if request_id else ""

        if response.status_code == 401:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "Authentication failed")
                raise AuthenticationError(
                    f"Authentication failed - {error_message}{request_id_info}"
                )
            except (ValueError, AttributeError, TypeError):
                raise AuthenticationError(
                    f"Authentication failed - unable to parse error "
                    f"response{request_id_info}"
                )
        elif response.status_code == 422:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "Request validation failed")
                raise ValidationError(f"{error_message}{request_id_info}")
            except (ValueError, AttributeError, TypeError):
                raise ValidationError(f"Request validation failed{request_id_info}")
        elif response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded{request_id_info}")
        elif response.status_code >= 500:
            raise ServerError(f"Server error: {response.status_code}{request_id_info}")
        else:
            raise LangChainAPIError(
                f"Unexpected status code: {response.status_code}{request_id_info}"
            )

    def _make_api_request(
        self, query: str, egnyte_user_token: str, search_options: EgnyteSearchOptions
    ) -> Dict[str, Any]:
        """Make direct API request to Egnyte hybrid search endpoint."""

        # Validate inputs
        self._validate_request_inputs(query, egnyte_user_token)

        # Prepare request data and headers
        request_data, headers = self._get_request_data(
            query, egnyte_user_token, search_options
        )

        # Make API request
        try:
            logger.info(
                f"Making API request to {self.base_url}/pubapi/v1/hybrid-search"
            )
            response = self._http_client.post(
                f"{self.base_url}/pubapi/v1/hybrid-search",
                json=request_data,
                headers=headers,
            )

            # Handle response
            return self._handle_response(response)

        except httpx.TimeoutException:
            raise TimeoutError("Request timed out")
        except httpx.ConnectError:
            raise ConnectionError("Failed to connect to API")
        except httpx.HTTPError as e:
            raise LangChainAPIError(f"HTTP error: {str(e)}")

    def _process_response_documents(
        self, response_data: Dict[str, Any]
    ) -> List[Document]:
        """
        Process API response data and convert to LangChain Documents.

        Args:
            response_data: The JSON response data from the API

        Returns:
            List of LangChain Document objects
        """
        documents: List[Document] = []
        docs_data = response_data.get("documents", [])
        if not docs_data:
            return documents

        for doc_data in docs_data:
            # Extract content and metadata
            content = doc_data.get("content", "")
            metadata_raw = doc_data.get("metadata", {})

            # Create LangChain Document
            langchain_doc = Document(
                page_content=content,
                metadata={
                    "source": metadata_raw.get("source", "egnyte"),
                    "title": metadata_raw.get("title", ""),
                    "file_path": metadata_raw.get("file_path", ""),
                    "entry_id": metadata_raw.get("entry_id", ""),
                    "score": metadata_raw.get("score", 0.0),
                    "created_at": metadata_raw.get("created_at"),
                    "modified_at": metadata_raw.get("modified_at"),
                    "size": metadata_raw.get("size"),
                    "content_type": metadata_raw.get("content_type", ""),
                    **metadata_raw.get("extra", {}),  # Include any extra metadata
                },
            )
            documents.append(langchain_doc)

        return documents

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,  # noqa: ARG002
        **kwargs: Any,
    ) -> List[Document]:
        """
        Retrieve relevant documents for the given query.

        This is the core method that LangChain calls for document retrieval.
        It looks for egnyte_user_token in kwargs to perform authentication.

        Args:
            query: The search query
            run_manager: The callback manager (provided by BaseRetriever)
            **kwargs: Additional parameters, must include 'egnyte_user_token'

        Returns:
            List of LangChain Document objects

        Raises:
            LangChainAPIError: When egnyte_user_token is not provided in kwargs
        """
        # Extract token from kwargs
        egnyte_user_token = kwargs.get("egnyte_user_token")
        if not egnyte_user_token:
            raise ValueError("egnyte_user_token is required. Provide it in kwargs:\n")

        # Extract search options from kwargs if provided
        search_options = kwargs.get("search_options", EgnyteSearchOptions())

        # Handle k parameter (number of documents to return)
        k = kwargs.get("k", self.k)
        if k != search_options.limit:
            # Create new search options with the k limit
            search_options = EgnyteSearchOptions(
                limit=k,
                folderPath=search_options.folderPath,
                collectionId=search_options.collectionId,
                createdBy=search_options.createdBy,
                createdAfter=search_options.createdAfter,
                createdBefore=search_options.createdBefore,
                preferredFolderPath=search_options.preferredFolderPath,
                excludeFolderPaths=search_options.excludeFolderPaths,
                folderPaths=search_options.folderPaths,
                entryIds=search_options.entryIds,
            )

        # Call the auth method with extracted parameters
        return self.get_relevant_documents_with_auth(
            query=query,
            egnyte_user_token=egnyte_user_token,
            search_options=search_options,
        )

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,  # noqa: ARG002
        **kwargs: Any,
    ) -> List[Document]:
        """
        Asynchronously retrieve relevant documents for the given query.

        This is the async version of _get_relevant_documents that LangChain calls
        for async document retrieval.

        Args:
            query: The search query
            run_manager: The async callback manager (provided by BaseRetriever)
            **kwargs: Additional parameters, must include 'egnyte_user_token'

        Returns:
            List of LangChain Document objects

        Raises:
            LangChainAPIError: When egnyte_user_token is not provided in kwargs
        """
        # Extract token from kwargs
        egnyte_user_token = kwargs.get("egnyte_user_token")
        if not egnyte_user_token:
            raise ValueError("egnyte_user_token is required. Provide it in kwargs:\n")

        # Extract search options from kwargs if provided
        search_options = kwargs.get("search_options", EgnyteSearchOptions())

        # Handle k parameter (number of documents to return)
        k = kwargs.get("k", self.k)
        if k != search_options.limit:
            # Create new search options with the k limit
            search_options = EgnyteSearchOptions(
                limit=k,
                folderPath=search_options.folderPath,
                collectionId=search_options.collectionId,
                createdBy=search_options.createdBy,
                createdAfter=search_options.createdAfter,
                createdBefore=search_options.createdBefore,
                preferredFolderPath=search_options.preferredFolderPath,
                excludeFolderPaths=search_options.excludeFolderPaths,
                folderPaths=search_options.folderPaths,
                entryIds=search_options.entryIds,
            )

        # Call the async auth method with extracted parameters
        return await self.aget_relevant_documents_with_auth(
            query=query,
            egnyte_user_token=egnyte_user_token,
            search_options=search_options,
        )

    def get_relevant_documents_with_auth(
        self,
        query: str,
        egnyte_user_token: str,
        search_options: Optional[EgnyteSearchOptions] = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents with authentication provided per call.

        Args:
            query: The search query
            egnyte_user_token: Egnyte user authentication token (MANDATORY)
            search_options: Search configuration options (optional)

        Returns:
            List of LangChain Document objects
        """
        # Use default search options if not provided
        if search_options is None:
            search_options = EgnyteSearchOptions()

        try:
            # Make direct API call
            response_data = self._make_api_request(
                query, egnyte_user_token, search_options
            )

            # Convert to LangChain Documents using helper method
            return self._process_response_documents(response_data)

        except (ValidationError, AuthenticationError) as e:
            # Re-raise validation and authentication errors as-is
            raise e
        except Exception as e:
            raise LangChainAPIError(f"Retrieval failed: {str(e)}")

    async def aget_relevant_documents_with_auth(
        self,
        query: str,
        egnyte_user_token: str,
        search_options: Optional[EgnyteSearchOptions] = None,
    ) -> List[Document]:
        """
        Asynchronously retrieve relevant documents with authentication provided
        per call.

        Args:
            query: The search query
            egnyte_user_token: Egnyte user authentication token (MANDATORY)
            search_options: Search configuration options (optional)

        Returns:
            List of LangChain Document objects
        """
        # Use default search options if not provided
        if search_options is None:
            search_options = EgnyteSearchOptions()

        try:
            # Make async API call
            response_data = await self._amake_api_request(
                query, egnyte_user_token, search_options
            )

            # Convert to LangChain Documents using helper method
            return self._process_response_documents(response_data)

        except (ValidationError, AuthenticationError) as e:
            # Re-raise validation and authentication errors as-is
            raise e
        except Exception as e:
            raise LangChainAPIError(f"Async retrieval failed: {str(e)}")

    async def _amake_api_request(
        self, query: str, egnyte_user_token: str, search_options: EgnyteSearchOptions
    ) -> Dict[str, Any]:
        """Make async API request to Egnyte hybrid search endpoint."""

        # Validate inputs
        self._validate_request_inputs(query, egnyte_user_token)

        # Prepare request data and headers
        request_data, headers = self._get_request_data(
            query, egnyte_user_token, search_options
        )

        # Make async API request
        try:
            logger.info(
                f"Making async API request to {self.base_url}/pubapi/v1/hybrid-search"
            )

            # Create async client for this request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/pubapi/v1/hybrid-search",
                    json=request_data,
                    headers=headers,
                )

                # Handle response
                return self._handle_response(response)

        except httpx.TimeoutException:
            raise TimeoutError("Async request timed out")
        except httpx.ConnectError:
            raise ConnectionError("Failed to connect to API")
        except httpx.HTTPError as e:
            raise LangChainAPIError(f"Async HTTP error: {str(e)}")

    def close(self) -> None:
        """Close the HTTP clients."""
        if hasattr(self, "_http_client"):
            self._http_client.close()

    def __del__(self) -> None:
        """Cleanup when object is destroyed."""
        self.close()


def create_retriever_tool(
    retriever: EgnyteRetriever, name: str, description: str, egnyte_user_token: str
) -> Any:
    """
    Create a LangChain tool from the EgnyteRetriever.

    This function creates a tool that can be used with LangChain agents.
    Since the new retriever design requires egnyte_user_token per call,
    this function creates a custom tool that includes the token.

    Args:
        retriever: The EgnyteRetriever instance
        name: Name of the tool
        description: Description of what the tool does
        egnyte_user_token: Egnyte user authentication token (required for API calls)

    Returns:
        LangChain tool object that includes the user token
    """
    try:
        from langchain.tools import Tool

        def search_egnyte(query: str) -> str:
            """Search Egnyte documents and return formatted results."""
            try:
                documents = retriever.get_relevant_documents_with_auth(
                    query=query, egnyte_user_token=egnyte_user_token
                )

                if not documents:
                    return "No documents found for the given query."

                results = []
                for i, doc in enumerate(documents, 1):
                    title = doc.metadata.get("title", "Unknown Document")
                    results.append(f"{i}. {title}\n   {doc.page_content}\n")

                return "\n".join(results)

            except Exception as e:
                return f"Error searching documents: {str(e)}"

        return Tool(name=name, description=description, func=search_egnyte)

    except ImportError:
        raise ImportError(
            "LangChain is required to create retriever tools. "
            "Install it with: pip install langchain>=0.1.0\n"
            "or: pip install langchain-core>=0.1.0"
        )

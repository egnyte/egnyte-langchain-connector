"""
Egnyte LangChain SDK

A Python SDK for integrating Egnyte document retrieval with LangChain
applications.

Copyright: Copyright (c) 2025 Egnyte Inc.

This package provides a comprehensive SDK for LangChain integration with
Egnyte document retrieval services. It offers both direct API access and
LangChain-compatible retrievers for seamless integration with LangChain
applications.

IMPORTANT: This SDK requires LangChain as a mandatory dependency.
The EgnyteRetriever class will not work without LangChain installed.

Classes:
    EgnyteRetriever: LangChain-compatible retriever class (REQUIRES LangChain)
    EgnyteSearchOptions: Configuration options for search behavior

Functions:
    create_retriever_tool: Create LangChain agent tools from retrievers

Usage:
    # LangChain-style retriever (REQUIRES LangChain)
    from egnyte_retriever import EgnyteRetriever

    # Initialize with domain only
    retriever = EgnyteRetriever(base_url="https://company.egnyte.com")

    # Provide token per call
    documents = retriever.invoke(
        query="machine learning",
        egnyte_user_token="your-token"  # REQUIRED per call
    )

Requirements:
    - Python 3.11+
    - httpx>=0.24.0
    - pydantic>=2.0.0
    - langchain-core>=0.1.0 (REQUIRED for EgnyteRetriever)
    - langchain>=0.1.0 (REQUIRED for EgnyteRetriever)

Version: 0.0.2
"""

# Comprehensive exception handling
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    LangChainAPIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)

# LangChain-style imports (primary interface)
from .retriever import EgnyteRetriever, create_retriever_tool

# Utility functions for common patterns
from .utilities import (
    EgnyteSearchOptions,
    create_date_range_search_options,
    create_folder_search_options,
)

# Package metadata
__version__ = "0.0.2"
__author__ = "Abhishek Shahdeo"
__email__ = "ashahdeo@egnyte.com"

# LangChain-style exports (follows langchain-box pattern)
__all__ = [
    # Core retriever (primary interface)
    "EgnyteRetriever",
    # Configuration and utilities (LangChain pattern)
    "EgnyteSearchOptions",
    # Tool creation (agent integration)
    "create_retriever_tool",
    # Utility functions (convenience)
    "create_folder_search_options",
    "create_date_range_search_options",
    # Comprehensive error handling
    "LangChainAPIError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "ConnectionError",
]

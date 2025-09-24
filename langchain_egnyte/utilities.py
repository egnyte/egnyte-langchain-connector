"""Utilities and configuration classes for Egnyte retriever.

Application: Egnyte LangChain Retriever
Copyright: Copyright (c) 2025 Egnyte Inc.

This module provides configuration classes and utilities for the Egnyte
retriever, following LangChain patterns while maintaining comprehensive
functionality.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class EgnyteSearchOptions(BaseModel):
    """Configuration options for Egnyte hybrid search operations.

    This class provides comprehensive configuration options for filtering and
    customizing search behavior when using the EgnyteRetriever. It follows
    LangChain patterns while providing extensive Egnyte-specific functionality.

    Example:
        Basic usage:

        .. code-block:: python

            from egnyte_retriever import EgnyteSearchOptions

            # Simple configuration
            search_options = EgnyteSearchOptions(
                limit=50,
                folder_path="/policies"
            )

            # Advanced configuration
            search_options = EgnyteSearchOptions(
                limit=100,
                folderPath="/documents",
                createdAfter=1640995200000,  # Unix timestamp in milliseconds
                createdBy="john.doe",
                preferredFolderPath="/important",
                excludeFolderPaths=["/temp", "/archive"]
            )

    Integration with LangChain:
        This class is designed to work seamlessly with LangChain retrievers:

        .. code-block:: python

            from egnyte_retriever import EgnyteRetriever, EgnyteSearchOptions
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            # Configure search options
            search_options = EgnyteSearchOptions(
                limit=20,
                folderPath="/policies",
                createdAfter=1672531200000
            )

            # Create retriever with options
            retriever = EgnyteRetriever(
                base_url="https://company.egnyte.com",
                search_options=search_options
            )

            # Use in LangChain chain
            llm = ChatOpenAI(model="gpt-4")
            chain = retriever | prompt | llm
    """

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of results to return. Must be between 1 "
        "and 1000.",
    )

    folderPath: Optional[str] = Field(
        default=None,
        description="Restricts search to a specific folder path. Must be a "
        "valid CFS filesystem path.",
    )

    collectionId: Optional[str] = Field(
        default=None,
        description="Restricts search to a specific collection (KBA).",
    )

    createdBy: Optional[str] = Field(
        default=None,
        description="Filters results by creator username. Must be a user "
        "the requester can access.",
    )

    createdAfter: Optional[int] = Field(
        default=None,
        description="Filters results to items created after this timestamp "
        "(Unix epoch in milliseconds).",
    )

    createdBefore: Optional[int] = Field(
        default=None,
        description="Filters results to items created before this timestamp "
        "(Unix epoch in milliseconds).",
    )

    preferredFolderPath: Optional[str] = Field(
        default=None, description="Boosts results from this folder path."
    )

    excludeFolderPaths: Optional[List[str]] = Field(
        default=None, description="Excludes results from these folder paths."
    )

    folderPaths: Optional[List[str]] = Field(
        default=None, description="Includes results only from these folder paths."
    )

    entryIds: Optional[List[str]] = Field(
        default=None, description="Restricts search to specific entry IDs."
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    @field_validator("folderPath", "preferredFolderPath")
    @classmethod
    def validate_folder_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate individual folder paths."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Folder path cannot be empty")
            if not v.startswith("/"):
                raise ValueError("Folder path must start with '/'")
            if v.endswith("/") and len(v) > 1:
                v = v.rstrip("/")  # Remove trailing slash except for root
            if "//" in v:
                raise ValueError("Folder path cannot contain consecutive slashes")
        return v

    @field_validator("excludeFolderPaths", "folderPaths")
    @classmethod
    def validate_folder_path_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate folder path lists."""
        if v is not None:
            if not v:  # Empty list
                raise ValueError("Folder path list cannot be empty")

            validated_paths = []
            for i, path in enumerate(v):
                if not isinstance(path, str):
                    raise ValueError(f"Folder path at index {i} must be a string")

                path = path.strip()
                if not path:
                    raise ValueError(f"Folder path at index {i} cannot be empty")
                if not path.startswith("/"):
                    raise ValueError(f"Folder path at index {i} must start with '/'")
                if path.endswith("/") and len(path) > 1:
                    path = path.rstrip("/")  # Remove trailing slash except for root
                if "//" in path:
                    raise ValueError(
                        f"Folder path at index {i} cannot contain consecutive slashes"
                    )

                validated_paths.append(path)

            # Check for duplicates
            if len(set(validated_paths)) != len(validated_paths):
                raise ValueError("Folder path list cannot contain duplicates")

            return validated_paths
        return v

    @field_validator("createdBy")
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate created_by username."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Username cannot be empty")
            if len(v) > 255:
                raise ValueError("Username cannot exceed 255 characters")
            # Basic username validation (alphanumeric, dots, hyphens, underscores)
            import re

            if not re.match(r"^[a-zA-Z0-9._-]+$", v):
                raise ValueError(
                    "Username can only contain letters, numbers, dots, "
                    "hyphens, and underscores"
                )
        return v

    @field_validator("createdAfter")
    @classmethod
    def validate_created_after(cls, v: Optional[int]) -> Optional[int]:
        """Validate createdAfter timestamp values."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("Timestamp must be an integer")
            if v < 0:
                raise ValueError("Timestamp cannot be negative")
            # Check if timestamp is reasonable (not too far in the future)
            import time

            current_time_ms = int(time.time() * 1000)
            # Allow up to 10 years in the future
            max_future_time = current_time_ms + (10 * 365 * 24 * 60 * 60 * 1000)
            if v > max_future_time:
                raise ValueError("Timestamp is too far in the future")
        return v

    @field_validator("createdBefore")
    @classmethod
    def validate_created_before(cls, v: Optional[int]) -> Optional[int]:
        """Validate createdBefore timestamp values."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("Timestamp must be an integer")
            if v < 0:
                raise ValueError("Timestamp cannot be negative")
            # No future date validation for createdBefore since it's an upper bound
        return v

    @field_validator("collectionId")
    @classmethod
    def validate_collection_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate collection ID."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Collection ID cannot be empty")
            if len(v) > 100:
                raise ValueError("Collection ID cannot exceed 100 characters")
        return v

    @field_validator("entryIds")
    @classmethod
    def validate_entry_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate entry IDs list."""
        if v is not None:
            if not v:  # Empty list
                raise ValueError("Entry IDs list cannot be empty")

            validated_ids = []
            for i, entry_id in enumerate(v):
                if not isinstance(entry_id, str):
                    raise ValueError(f"Entry ID at index {i} must be a string")

                entry_id = entry_id.strip()
                if not entry_id:
                    raise ValueError(f"Entry ID at index {i} cannot be empty")
                if len(entry_id) > 50:
                    raise ValueError(
                        f"Entry ID at index {i} cannot exceed 50 characters"
                    )

                validated_ids.append(entry_id)

            # Check for duplicates
            if len(set(validated_ids)) != len(validated_ids):
                raise ValueError("Entry IDs list cannot contain duplicates")

            # Reasonable limit on number of entry IDs
            if len(validated_ids) > 100:
                raise ValueError("Cannot specify more than 100 entry IDs")

            return validated_ids
        return v

    @model_validator(mode="after")
    def validate_model(self) -> "EgnyteSearchOptions":
        """Validate the entire model for business logic constraints."""
        # Validate timestamp order
        if self.createdAfter and self.createdBefore:
            if self.createdAfter >= self.createdBefore:
                raise ValueError("createdAfter must be less than createdBefore")

            # Validate reasonable time range (not more than 10 years)
            time_diff_ms = self.createdBefore - self.createdAfter
            max_range_ms = 10 * 365 * 24 * 60 * 60 * 1000  # 10 years in milliseconds
            if time_diff_ms > max_range_ms:
                raise ValueError("Date range cannot exceed 10 years")

        # Validate folder path exclusivity
        if self.excludeFolderPaths and self.folderPaths:
            raise ValueError(
                "Cannot specify both excludeFolderPaths and folderPaths. "
                "Use one or the other for folder filtering."
            )

        # Validate folder path conflicts with specific folderPath
        if self.folderPath:
            if self.excludeFolderPaths and self.folderPath in self.excludeFolderPaths:
                raise ValueError(
                    f"folderPath '{self.folderPath}' cannot be in excludeFolderPaths"
                )
            if self.folderPaths and self.folderPath not in self.folderPaths:
                raise ValueError(
                    f"folderPath '{self.folderPath}' must be included in "
                    "folderPaths when both are specified"
                )

        # Validate preferred folder path conflicts
        if self.preferredFolderPath:
            if (
                self.excludeFolderPaths
                and self.preferredFolderPath in self.excludeFolderPaths
            ):
                raise ValueError(
                    f"preferredFolderPath '{self.preferredFolderPath}' "
                    "cannot be in excludeFolderPaths"
                )

        # Validate reasonable combinations
        if self.entryIds and (
            self.folderPath or self.folderPaths or self.excludeFolderPaths
        ):
            # This is allowed but might be inefficient, so we could warn
            # For now, we'll allow it as it might be a valid use case
            pass

        # Validate collectionId with folder restrictions
        if self.collectionId and (self.folderPath or self.folderPaths):
            # Collections might have their own folder restrictions
            # This is allowed but the user should be aware
            pass

        return self

    def to_dict(self) -> dict:
        """Convert search options to dictionary for API requests.

        Returns:
            Dictionary representation suitable for Egnyte API calls.
            Only includes fields that have been set (non-None values).
        """
        return self.model_dump(exclude_unset=True)

    @classmethod
    def for_folder(cls, folder_path: str, limit: int = 100) -> "EgnyteSearchOptions":
        """Create search options for a specific folder.

        Args:
            folder_path: The folder path to search within
            limit: Maximum number of results

        Returns:
            EgnyteSearchOptions configured for folder search
        """
        return cls(limit=limit, folderPath=folder_path)

    @classmethod
    def for_date_range(
        cls, created_after: int, created_before: int, limit: int = 100
    ) -> "EgnyteSearchOptions":
        """Create search options for a date range.

        Args:
            created_after: Start timestamp (Unix epoch in milliseconds)
            created_before: End timestamp (Unix epoch in milliseconds)
            limit: Maximum number of results

        Returns:
            EgnyteSearchOptions configured for date range search
        """
        return cls(
            limit=limit, createdAfter=created_after, createdBefore=created_before
        )

    @classmethod
    def for_user(cls, username: str, limit: int = 100) -> "EgnyteSearchOptions":
        """Create search options for documents by a specific user.

        Args:
            username: The username to filter by
            limit: Maximum number of results

        Returns:
            EgnyteSearchOptions configured for user search
        """
        return cls(limit=limit, createdBy=username)


# Utility functions for common operations
def create_folder_search_options(
    folder_path: str, limit: int = 100
) -> EgnyteSearchOptions:
    """Create search options for folder-based search.

    This is a convenience function that creates EgnyteSearchOptions
    configured for searching within a specific folder.

    Args:
        folder_path: The folder path to search within
        limit: Maximum number of results to return

    Returns:
        Configured EgnyteSearchOptions instance

    Example:
        .. code-block:: python

            from egnyte_retriever.utilities import create_folder_search_options

            options = create_folder_search_options("/Shared/Policies", limit=50)
    """
    return EgnyteSearchOptions.for_folder(folder_path, limit)


def create_date_range_search_options(
    start_date: int, end_date: int, limit: int = 100
) -> EgnyteSearchOptions:
    """Create search options for date range search.

    Args:
        start_date: Start timestamp (Unix epoch in milliseconds)
        end_date: End timestamp (Unix epoch in milliseconds)
        limit: Maximum number of results to return

    Returns:
        Configured EgnyteSearchOptions instance

    Example:
        .. code-block:: python

            from egnyte_retriever.utilities import create_date_range_search_options

            # Search for documents from 2023
            options = create_date_range_search_options(
                1672531200000,  # Jan 1, 2023
                1704067200000,  # Jan 1, 2024
                limit=100
            )
    """
    return EgnyteSearchOptions.for_date_range(start_date, end_date, limit)

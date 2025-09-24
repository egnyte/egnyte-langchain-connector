"""Tests for EgnyteSearchOptions and utility functions."""

import pytest

from langchain_egnyte.utilities import EgnyteSearchOptions


class TestEgnyteSearchOptions:
    """Test cases for EgnyteSearchOptions."""

    def test_default_initialization(self):
        """Test default initialization of search options."""
        options = EgnyteSearchOptions()

        assert options.limit == 100
        assert options.folderPath is None
        assert options.collectionId is None
        assert options.createdBy is None
        assert options.createdAfter is None
        assert options.createdBefore is None
        assert options.preferredFolderPath is None
        assert options.excludeFolderPaths is None
        assert options.folderPaths is None
        assert options.entryIds is None

    def test_custom_initialization(self):
        """Test custom initialization with all parameters."""
        options = EgnyteSearchOptions(
            limit=50,
            folderPath="/test",
            collectionId="123",
            createdBy="user.name",
            createdAfter=1640995200000,  # 2022-01-01
            createdBefore=1672531200000,  # 2023-01-01
            preferredFolderPath="/preferred",
            excludeFolderPaths=["/exclude1", "/exclude2"],
            entryIds=["id1", "id2"],
        )

        assert options.limit == 50
        assert options.folderPath == "/test"
        assert options.collectionId == "123"
        assert options.createdBy == "user.name"
        assert options.createdAfter == 1640995200000
        assert options.createdBefore == 1672531200000
        assert options.preferredFolderPath == "/preferred"
        assert options.excludeFolderPaths == ["/exclude1", "/exclude2"]
        # folder_paths not set since we used exclude_folder_paths
        assert options.folderPaths is None
        assert options.entryIds == ["id1", "id2"]

    def test_limit_validation_valid(self):
        """Test valid limit values."""
        # Test minimum valid limit
        options = EgnyteSearchOptions(limit=1)
        assert options.limit == 1

        # Test maximum valid limit
        options = EgnyteSearchOptions(limit=1000)
        assert options.limit == 1000

        # Test typical limit
        options = EgnyteSearchOptions(limit=100)
        assert options.limit == 100

    def test_limit_validation_invalid(self):
        """Test invalid limit values."""
        # Test limit too low
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(limit=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Test limit too high
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(limit=1001)
        assert "Input should be less than or equal to 1000" in str(exc_info.value)

        # Test negative limit
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(limit=-1)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_folder_path_validation_valid(self):
        """Test valid folder path formats."""
        # Test absolute path
        options = EgnyteSearchOptions(folderPath="/Shared/Documents")
        assert options.folderPath == "/Shared/Documents"

        # Test root path
        options = EgnyteSearchOptions(folderPath="/")
        assert options.folderPath == "/"

        # Test nested path
        options = EgnyteSearchOptions(folderPath="/Private/User/Projects")
        assert options.folderPath == "/Private/User/Projects"

    def test_folder_path_validation_invalid(self):
        """Test invalid folder path formats."""
        # Test relative path
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(folderPath="relative/path")
        assert "Folder path must start with '/'" in str(exc_info.value)

        # Test empty string
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(folderPath="")
        assert "Folder path cannot be empty" in str(exc_info.value)

    def test_preferred_folder_path_validation(self):
        """Test preferred folder path validation."""
        # Valid preferred folder path
        options = EgnyteSearchOptions(preferredFolderPath="/Shared")
        assert options.preferredFolderPath == "/Shared"

        # Invalid preferred folder path
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(preferredFolderPath="relative")
        assert "Folder path must start with '/'" in str(exc_info.value)

    def test_exclude_folder_paths_validation(self):
        """Test exclude folder paths validation."""
        # Valid exclude paths
        options = EgnyteSearchOptions(excludeFolderPaths=["/temp", "/archive"])
        assert options.excludeFolderPaths == ["/temp", "/archive"]

        # Invalid exclude path
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(excludeFolderPaths=["/valid", "invalid"])
        assert "Folder path at index 1 must start with '/'" in str(exc_info.value)

    def test_folder_paths_validation(self):
        """Test folder paths validation."""
        # Valid folder paths
        options = EgnyteSearchOptions(folderPaths=["/docs", "/images"])
        assert options.folderPaths == ["/docs", "/images"]

        # Invalid folder path
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(folderPaths=["/valid", "invalid"])
        assert "Folder path at index 1 must start with '/'" in str(exc_info.value)

    def test_created_after_validation(self):
        """Test created_after timestamp validation."""
        # Valid timestamp
        timestamp = 1640995200000  # 2022-01-01
        options = EgnyteSearchOptions(createdAfter=timestamp)
        assert options.createdAfter == timestamp

        # Invalid timestamp (negative)
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(createdAfter=-1)
        assert "Timestamp cannot be negative" in str(exc_info.value)

    def test_created_before_validation(self):
        """Test created_before timestamp validation."""
        # Valid timestamp
        timestamp = 1672531200000  # 2023-01-01
        options = EgnyteSearchOptions(createdBefore=timestamp)
        assert options.createdBefore == timestamp

        # Invalid timestamp (negative)
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(createdBefore=-1)
        assert "Timestamp cannot be negative" in str(exc_info.value)

    def test_date_range_validation(self):
        """Test date range validation (created_after < created_before)."""
        # Valid date range
        options = EgnyteSearchOptions(
            createdAfter=1640995200000,  # 2022-01-01
            createdBefore=1672531200000,  # 2023-01-01
        )
        assert options.createdAfter == 1640995200000
        assert options.createdBefore == 1672531200000

        # Invalid date range (after > before)
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(
                createdAfter=1672531200000,  # 2023-01-01
                createdBefore=1640995200000,  # 2022-01-01
            )
        assert "createdAfter must be less than createdBefore" in str(exc_info.value)

    def test_entry_ids_validation(self):
        """Test entry IDs validation."""
        # Valid entry IDs
        options = EgnyteSearchOptions(entryIds=["id1", "id2", "id3"])
        assert options.entryIds == ["id1", "id2", "id3"]

        # Empty entry IDs list (invalid)
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(entryIds=[])
        assert "Entry IDs list cannot be empty" in str(exc_info.value)

        # Non-string entry ID
        with pytest.raises(ValueError) as exc_info:
            EgnyteSearchOptions(entryIds=["valid", 123])
        assert "Input should be a valid string" in str(exc_info.value)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        options = EgnyteSearchOptions(limit=50, folderPath="/test", collectionId="123")

        result = options.to_dict()

        assert result["limit"] == 50
        assert result["folderPath"] == "/test"
        assert result["collectionId"] == "123"
        # None values should not be included
        assert "createdBy" not in result
        assert "createdAfter" not in result

    def test_to_dict_exclude_none(self):
        """Test dictionary conversion excludes unset values."""
        # Only set some values, leave others unset
        options = EgnyteSearchOptions(limit=100, collectionId="123")

        result = options.to_dict()

        assert result["limit"] == 100
        assert result["collectionId"] == "123"
        # Unset values should not be in the result
        assert "folderPath" not in result
        assert "createdBy" not in result

    def test_to_dict_include_non_empty_lists(self):
        """Test dictionary conversion includes non-empty lists."""
        options = EgnyteSearchOptions(folderPaths=["/test"], entryIds=["id1", "id2"])

        result = options.to_dict()

        # Non-empty lists should be included
        assert result["folderPaths"] == ["/test"]
        assert result["entryIds"] == ["id1", "id2"]

    def test_repr(self):
        """Test string representation."""
        options = EgnyteSearchOptions(limit=50, folderPath="/test")
        repr_str = repr(options)

        assert "EgnyteSearchOptions" in repr_str
        assert "limit=50" in repr_str
        assert "folderPath='/test'" in repr_str

    def test_equality(self):
        """Test equality comparison."""
        options1 = EgnyteSearchOptions(limit=50, folderPath="/test")
        options2 = EgnyteSearchOptions(limit=50, folderPath="/test")
        options3 = EgnyteSearchOptions(limit=100, folderPath="/test")

        assert options1 == options2
        assert options1 != options3

    def test_copy_with_modifications(self):
        """Test creating a copy with modifications."""
        original = EgnyteSearchOptions(limit=50, folderPath="/test")

        # Create a copy with different limit
        modified = EgnyteSearchOptions(
            limit=100,
            folderPath=original.folderPath,
            collectionId=original.collectionId,
            createdBy=original.createdBy,
            createdAfter=original.createdAfter,
            createdBefore=original.createdBefore,
            preferredFolderPath=original.preferredFolderPath,
            excludeFolderPaths=original.excludeFolderPaths,
            folderPaths=original.folderPaths,
            entryIds=original.entryIds,
        )

        assert modified.limit == 100
        assert modified.folderPath == "/test"
        assert original.limit == 50  # Original unchanged

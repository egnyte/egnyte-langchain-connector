"""Sample API responses for testing."""

# Sample successful search response
SAMPLE_SEARCH_RESPONSE = {
    "results": [
        {
            "name": "project_proposal.pdf",
            "path": "/Shared/Documents/project_proposal.pdf",
            "size": 2048576,
            "lastModified": "2023-12-01T10:30:00Z",
            "created": "2023-11-15T09:00:00Z",
            "createdBy": "john.doe@company.com",
            "type": "file",
            "entryId": "abc123def456",
            "parentId": "parent789",
            "isFolder": False,
            "mimeType": "application/pdf",
        },
        {
            "name": "meeting_notes.docx",
            "path": "/Private/john.doe/meeting_notes.docx",
            "size": 524288,
            "lastModified": "2023-12-02T14:15:00Z",
            "created": "2023-12-02T14:00:00Z",
            "createdBy": "john.doe@company.com",
            "type": "file",
            "entryId": "def456ghi789",
            "parentId": "parent456",
            "isFolder": False,
            "mimeType": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        },
        {
            "name": "presentation.pptx",
            "path": "/Shared/Presentations/presentation.pptx",
            "size": 8388608,
            "lastModified": "2023-11-28T16:45:00Z",
            "created": "2023-11-20T11:30:00Z",
            "createdBy": "jane.smith@company.com",
            "type": "file",
            "entryId": "ghi789jkl012",
            "parentId": "parent123",
            "isFolder": False,
            "mimeType": (
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
        },
    ],
    "totalCount": 3,
    "offset": 0,
    "hasMore": False,
}

# Sample empty search response
EMPTY_SEARCH_RESPONSE = {"results": [], "totalCount": 0, "offset": 0, "hasMore": False}

# Sample large search response with pagination
LARGE_SEARCH_RESPONSE = {
    "results": [
        {
            "name": f"document_{i:03d}.pdf",
            "path": f"/Shared/Archive/document_{i:03d}.pdf",
            "size": 1024000 + i * 1000,
            "lastModified": f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z",
            "created": f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z",
            "createdBy": f"user{i % 5}@company.com",
            "type": "file",
            "entryId": f"entry_{i:06d}",
            "parentId": "archive_parent",
            "isFolder": False,
            "mimeType": "application/pdf",
        }
        for i in range(100)
    ],
    "totalCount": 250,
    "offset": 0,
    "hasMore": True,
}

# Sample folder search response
FOLDER_SEARCH_RESPONSE = {
    "results": [
        {
            "name": "Projects",
            "path": "/Shared/Projects",
            "size": 0,
            "lastModified": "2023-12-01T00:00:00Z",
            "created": "2023-01-01T00:00:00Z",
            "createdBy": "admin@company.com",
            "type": "folder",
            "entryId": "folder_projects",
            "parentId": "shared_root",
            "isFolder": True,
            "mimeType": None,
        },
        {
            "name": "Archive",
            "path": "/Shared/Archive",
            "size": 0,
            "lastModified": "2023-11-15T00:00:00Z",
            "created": "2023-01-01T00:00:00Z",
            "createdBy": "admin@company.com",
            "type": "folder",
            "entryId": "folder_archive",
            "parentId": "shared_root",
            "isFolder": True,
            "mimeType": None,
        },
    ],
    "totalCount": 2,
    "offset": 0,
    "hasMore": False,
}

# Sample error responses
AUTHENTICATION_ERROR_RESPONSE = {
    "error": "unauthorized",
    "message": "Invalid or expired access token",
    "code": "INVALID_TOKEN",
    "timestamp": "2023-12-03T10:00:00Z",
}

VALIDATION_ERROR_RESPONSE = {
    "error": "validation_failed",
    "message": "Request validation failed",
    "errors": [
        {"field": "query", "message": "Query parameter is required"},
        {"field": "limit", "message": "Limit must be between 1 and 1000"},
    ],
    "code": "VALIDATION_ERROR",
    "timestamp": "2023-12-03T10:00:00Z",
}

NOT_FOUND_ERROR_RESPONSE = {
    "error": "not_found",
    "message": "The requested resource was not found",
    "resource": "/api/v2/search",
    "code": "RESOURCE_NOT_FOUND",
    "timestamp": "2023-12-03T10:00:00Z",
}

SERVER_ERROR_RESPONSE = {
    "error": "internal_server_error",
    "message": "An internal server error occurred",
    "code": "INTERNAL_ERROR",
    "timestamp": "2023-12-03T10:00:00Z",
    "requestId": "req_123456789",
}

RATE_LIMIT_ERROR_RESPONSE = {
    "error": "rate_limit_exceeded",
    "message": "API rate limit exceeded",
    "code": "RATE_LIMIT",
    "retryAfter": 60,
    "timestamp": "2023-12-03T10:00:00Z",
}

# Sample responses for different file types
IMAGE_FILES_RESPONSE = {
    "results": [
        {
            "name": "logo.png",
            "path": "/Shared/Images/logo.png",
            "size": 102400,
            "lastModified": "2023-11-20T12:00:00Z",
            "created": "2023-11-20T12:00:00Z",
            "createdBy": "designer@company.com",
            "type": "file",
            "entryId": "img_001",
            "parentId": "images_folder",
            "isFolder": False,
            "mimeType": "image/png",
        },
        {
            "name": "banner.jpg",
            "path": "/Shared/Images/banner.jpg",
            "size": 512000,
            "lastModified": "2023-11-22T15:30:00Z",
            "created": "2023-11-22T15:30:00Z",
            "createdBy": "designer@company.com",
            "type": "file",
            "entryId": "img_002",
            "parentId": "images_folder",
            "isFolder": False,
            "mimeType": "image/jpeg",
        },
    ],
    "totalCount": 2,
    "offset": 0,
    "hasMore": False,
}

SPREADSHEET_FILES_RESPONSE = {
    "results": [
        {
            "name": "budget_2023.xlsx",
            "path": "/Private/finance/budget_2023.xlsx",
            "size": 1048576,
            "lastModified": "2023-12-01T09:00:00Z",
            "created": "2023-01-01T09:00:00Z",
            "createdBy": "finance@company.com",
            "type": "file",
            "entryId": "xl_001",
            "parentId": "finance_folder",
            "isFolder": False,
            "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
        {
            "name": "sales_data.csv",
            "path": "/Shared/Reports/sales_data.csv",
            "size": 204800,
            "lastModified": "2023-11-30T17:00:00Z",
            "created": "2023-11-30T17:00:00Z",
            "createdBy": "sales@company.com",
            "type": "file",
            "entryId": "csv_001",
            "parentId": "reports_folder",
            "isFolder": False,
            "mimeType": "text/csv",
        },
    ],
    "totalCount": 2,
    "offset": 0,
    "hasMore": False,
}

# Sample response with special characters and Unicode
UNICODE_FILES_RESPONSE = {
    "results": [
        {
            "name": "résumé.pdf",
            "path": "/Private/hr/résumé.pdf",
            "size": 307200,
            "lastModified": "2023-11-25T14:00:00Z",
            "created": "2023-11-25T14:00:00Z",
            "createdBy": "hr@company.com",
            "type": "file",
            "entryId": "unicode_001",
            "parentId": "hr_folder",
            "isFolder": False,
            "mimeType": "application/pdf",
        },
        {
            "name": "文档.docx",
            "path": "/Shared/International/文档.docx",
            "size": 409600,
            "lastModified": "2023-11-26T10:30:00Z",
            "created": "2023-11-26T10:30:00Z",
            "createdBy": "international@company.com",
            "type": "file",
            "entryId": "unicode_002",
            "parentId": "intl_folder",
            "isFolder": False,
            "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
    ],
    "totalCount": 2,
    "offset": 0,
    "hasMore": False,
}

# Sample response with minimal metadata
MINIMAL_METADATA_RESPONSE = {
    "results": [
        {
            "name": "simple_file.txt",
            "path": "/Shared/simple_file.txt",
            "type": "file",
            "entryId": "minimal_001",
        }
    ],
    "totalCount": 1,
    "offset": 0,
    "hasMore": False,
}


# Helper function to create custom responses
def create_custom_response(
    file_count: int = 1,
    folder_path: str = "/Shared",
    file_prefix: str = "file",
    file_extension: str = "pdf",
    created_by: str = "user@company.com",
) -> dict:
    """Create a custom API response for testing.

    Args:
        file_count: Number of files to include in response
        folder_path: Base folder path for files
        file_prefix: Prefix for file names
        file_extension: File extension
        created_by: User who created the files

    Returns:
        Dictionary representing API response
    """
    results = []
    for i in range(file_count):
        file_name = f"{file_prefix}_{i:03d}.{file_extension}"
        results.append(
            {
                "name": file_name,
                "path": f"{folder_path}/{file_name}",
                "size": 1024 * (i + 1),
                "lastModified": f"2023-12-{(i % 30) + 1:02d}T10:00:00Z",
                "created": f"2023-11-{(i % 30) + 1:02d}T10:00:00Z",
                "createdBy": created_by,
                "type": "file",
                "entryId": f"custom_{i:06d}",
                "parentId": "custom_parent",
                "isFolder": False,
                "mimeType": f"application/{file_extension}",
            }
        )

    return {"results": results, "totalCount": file_count, "offset": 0, "hasMore": False}

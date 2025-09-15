# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive design documentation with visual diagrams
- Professional PNG diagrams for architecture, class hierarchy, data flow, package structure, and integration patterns

### Changed

- Enhanced documentation structure and visual references

## [0.0.1] - 2025-01-13

### Added

- Initial release of egnyte-retriever package
- EgnyteRetriever class with LangChain BaseRetriever compliance
- EgnyteSearchOptions for advanced search configuration with comprehensive filtering
- Comprehensive error handling with custom LangChain-compatible exceptions:
  - LangChainAPIError (base exception)
  - AuthenticationError (401 errors)
  - ValidationError (422 errors)
  - NotFoundError (404 errors)
  - NetworkError (connection issues)
- Tool creation utilities for LangChain agents via `create_retriever_tool`
- Full type safety with Pydantic v2 models and dataclasses
- Production-ready authentication with token-per-request model
- Multi-tenant support for enterprise deployments

### Features

- Hybrid search capabilities via Egnyte Public API v1
- Token-per-request authentication model for security
- Extensive search filtering options:
  - Folder path filtering (include/exclude)
  - Collection-based search
  - Date range filtering (created_after, created_before)
  - User-based filtering (created_by)
  - Entry ID specific retrieval
  - Result limiting and pagination
- LangChain chain and agent integration
- Async support for all retrieval operations
- Comprehensive test coverage with demo scripts
- Professional documentation with examples
- Visual architecture diagrams and design documentation

### Technical Details

- Built on LangChain Core v0.1.0+ for maximum compatibility
- Uses httpx for robust HTTP client operations
- Pydantic v2 for data validation and serialization
- Type hints throughout for IDE support and static analysis
- Modular architecture with clear separation of concerns

### Documentation

- Complete README with installation and usage instructions
- Comprehensive demo scripts covering all use cases
- Integration examples for chains and agents
- Error handling and troubleshooting guides
- Performance optimization recommendations

### Security

- Token-per-request authentication prevents token leakage
- Input validation for all search parameters
- Secure error handling without exposing sensitive information
- HTTPS-only communication with Egnyte API
- Rate limiting and retry logic for API stability

### Performance

- Efficient document processing and metadata extraction
- Configurable result limits to manage response sizes
- Async operations for non-blocking retrieval
- Connection pooling for improved throughput
- Optimized search parameter handling

### Compatibility

- Python 3.11+ support
- LangChain 0.1.0+ compatibility
- Cross-platform support (Windows, macOS, Linux)
- Enterprise Egnyte deployment compatibility
- Multi-region Egnyte instance support

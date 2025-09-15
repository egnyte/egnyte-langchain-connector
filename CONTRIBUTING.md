# Contributing to Egnyte Retriever

Thank you for your interest in contributing to the Egnyte Retriever package! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of LangChain framework
- Familiarity with Egnyte API (helpful but not required)

### Development Setup

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/langchain-egnyte.git
   cd langchain-egnyte
   ```

2. **Set up Development Environment**

   ### Option A: Using uv (Recommended - Fast & Modern)

   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install all dependencies
   uv sync --dev

   # Activate virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

   ### Option B: Using pip (Traditional)

   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Verify Installation**
   ```bash
   python -c "from egnyte_retriever import EgnyteRetriever; print('Installation successful!')"
   ```

## Making Changes

### Branch Naming Convention

- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation changes
- `refactor/description` - for code refactoring

### Development Workflow

1. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**

   - Follow the existing code structure
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**

   ### With uv (Recommended)

   ```bash
   # Run all tests
   uv run pytest

   # Run specific test file
   uv run pytest tests/test_retriever.py

   # Run with coverage
   uv run pytest --cov=egnyte_retriever

   # Format code
   uv run black .
   uv run isort .

   # Type checking
   uv run mypy .
   ```

   ### With pip (Traditional)

   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_retriever.py

   # Run with coverage
   pytest --cov=egnyte_retriever
   ```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── test_retriever.py          # Core retriever tests
├── test_utilities.py          # Search options tests
├── test_exceptions.py         # Error handling tests
├── integration/
│   ├── __init__.py
│   └── test_api_integration.py # Real API tests
└── fixtures/
    ├── __init__.py
    └── sample_responses.py     # Mock API responses
```

### Writing Tests

- Use pytest for all tests
- Mock external API calls for unit tests
- Include integration tests for real API scenarios
- Test both success and error cases
- Maintain high test coverage (aim for >90%)

### Running Tests

```bash
# Unit tests only
pytest tests/ -k "not integration"

# Integration tests (requires API credentials)
export EGNYTE_DOMAIN="your-domain.egnyte.com"
export EGNYTE_TOKEN="your-api-token"
pytest tests/integration/

# All tests
pytest
```

## Code Style

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use [mypy](https://mypy.readthedocs.io/) for type checking

### Code Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

### Type Hints

- Use type hints for all function parameters and return values
- Import types from `typing` module when needed
- Use `Optional[T]` for nullable parameters
- Use `List[T]`, `Dict[K, V]` for collections

### Documentation

- Use docstrings for all public functions and classes
- Follow Google-style docstring format
- Include examples in docstrings where helpful
- Keep documentation up to date with code changes

## Submitting Changes

### Pull Request Process

1. **Ensure Tests Pass**

   ```bash
   pytest
   black --check .
   isort --check-only .
   flake8 .
   mypy .
   ```

2. **Update Documentation**

   - Update README.md if needed
   - Update CHANGELOG.md with your changes
   - Add docstrings for new functions

3. **Create Pull Request**
   - Use a clear, descriptive title
   - Include a detailed description of changes
   - Reference any related issues
   - Add screenshots for UI changes (if applicable)

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Integration tests pass (if applicable)

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- Package version
- Operating system
- Minimal code example that reproduces the issue
- Full error traceback
- Expected vs actual behavior

### Feature Requests

For feature requests, please include:

- Clear description of the feature
- Use case and motivation
- Proposed API (if applicable)
- Any relevant examples or references

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed

## Development Guidelines

### Adding New Features

1. Discuss the feature in an issue first
2. Ensure it aligns with LangChain patterns
3. Add comprehensive tests
4. Update documentation
5. Consider backward compatibility

### Modifying Existing Code

1. Maintain backward compatibility when possible
2. Update tests to reflect changes
3. Update documentation
4. Consider performance implications

### Dependencies

- Minimize new dependencies
- Use well-maintained packages
- Pin versions appropriately
- Update requirements in pyproject.toml

## Getting Help

- Create an issue for questions
- Check existing issues and documentation
- Join LangChain community discussions
- Review the codebase for examples

Thank you for contributing to Egnyte Retriever!

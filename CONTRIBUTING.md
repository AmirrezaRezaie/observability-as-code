# Contributing to Observability as Code

Thank you for your interest in contributing to Observability as Code! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/AmirrezaRezaie/observability-as-code.git
   cd observability-as-code
   ```
3. **Install dependencies**:
   ```bash
   cd grafana-as-code
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   ```bash
   pytest
   ```

4. **Format your code**:
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

5. **Commit your changes** with a clear message

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Add **type hints** for new functions
- Write **docstrings** for all public functions and classes

### Example

```python
from typing import List, Optional
from src import GrafanaClient


def list_dashboards(
    client: GrafanaClient,
    folder_uid: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[dict]:
    """
    List dashboards with optional filtering.

    Args:
        client: Grafana API client instance
        folder_uid: Optional folder UID to filter by
        tags: Optional list of tags to filter by

    Returns:
        List of dashboard dictionaries containing uid, title, and folder info
    """
    # Implementation here
    pass
```

### Code Organization

- Keep functions focused and small
- Use descriptive variable names
- Add comments for complex logic
- Don't repeat yourself (DRY)

## Testing

### Writing Tests

- Write tests for all new features
- Use `pytest` for testing
- Mock external API calls
- Aim for high code coverage

### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from src import GrafanaClient, Dashboard


def test_dashboard_create():
    """Test dashboard creation with client."""
    with patch.object(GrafanaClient, 'post') as mock_post:
        mock_post.return_value = {
            "uid": "test-uid",
            "version": 1
        }

        client = GrafanaClient()
        dashboard = Dashboard.create(client, "Test Dashboard")

        assert dashboard.uid == "test-uid"
        assert dashboard.title == "Test Dashboard"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(dashboard): add duplicate method to Dashboard class

Fixes #123

Implement dashboard duplication with optional folder override
and automatic title generation.

feat(cli): add folder tree command

Displays hierarchical folder structure with dashboard counts
for better visualization of Grafana organization.

fix(datasource): handle missing datasource gracefully

Returns None instead of raising exception when datasource
not found, allowing for better error handling in calling code.

docs: update API reference with new examples

Add comprehensive examples for PanelComponent methods
including query editing and panel duplication.
```

## Submitting Changes

### Pull Request Guidelines

1. **Title** should follow commit message format
2. **Description** should:
   - Reference related issues (e.g., "Fixes #123")
   - Describe changes made
   - Include screenshots for UI changes
   - List breaking changes

3. **Checklist**:
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - - [ ] Documentation updated
   - [ ] Changelog updated (if applicable)
   - [ ] Commit messages follow conventions

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. Address review comments promptly
4. Keep PRs focused and small when possible

## Questions?

Feel free to open an issue with the `question` label if you need clarification or guidance.

---

Thank you for contributing to Observability as Code! 🚀

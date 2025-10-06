# Contributing to WIFIjam

Thank you for your interest in contributing to WIFIjam! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow ethical hacking principles
- Respect legal boundaries

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - OS and version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs
   - Screenshots if applicable

### Suggesting Features

1. Check if the feature has been suggested
2. Use the feature request template
3. Explain:
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Update documentation
6. Submit pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/WIFIjam.git
cd WIFIjam

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Coding Standards

### Python Style Guide

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters
- Use meaningful variable names

### Code Quality Tools

```bash
# Format code
black wifijam/

# Check style
flake8 wifijam/

# Type checking
mypy wifijam/

# Run all checks
make lint
```

### Example Code

```python
"""
Module docstring explaining purpose.
"""

from typing import Optional, List
from wifijam.core.logger import get_logger

logger = get_logger(__name__)


class ExampleClass:
    """
    Class docstring explaining purpose.
    
    Attributes:
        attribute_name: Description of attribute
    """
    
    def __init__(self, param: str):
        """
        Initialize the class.
        
        Args:
            param: Description of parameter
        """
        self.attribute_name = param
    
    def example_method(self, arg: int) -> Optional[str]:
        """
        Method docstring explaining what it does.
        
        Args:
            arg: Description of argument
        
        Returns:
            Description of return value
        
        Raises:
            ValueError: When arg is invalid
        """
        if arg < 0:
            raise ValueError("arg must be non-negative")
        
        logger.info(f"Processing arg: {arg}")
        return str(arg)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wifijam

# Run specific test
pytest tests/test_adapter.py

# Run with verbose output
pytest -v
```

### Writing Tests

```python
import pytest
from wifijam.wifi.adapter import AdapterManager


def test_adapter_manager_init():
    """Test AdapterManager initialization."""
    manager = AdapterManager()
    assert manager is not None
    assert isinstance(manager.adapters, list)


def test_adapter_detection():
    """Test adapter detection."""
    manager = AdapterManager()
    manager.refresh()
    # Add assertions based on expected behavior
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When parameters are invalid
        RuntimeError: When operation fails
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Updating Documentation

- Update README.md for user-facing changes
- Update API documentation for API changes
- Add examples for new features
- Update CHANGELOG.md

## Commit Messages

### Format

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(scanner): add 5GHz channel support

Added support for scanning 5GHz WiFi channels.
Includes channel list and frequency mapping.

Fixes #45

---

fix(monitor): handle monitor mode errors gracefully

Improved error handling when monitor mode fails.
Now provides clear error messages to users.

Fixes #67

---

docs(readme): update installation instructions

Added detailed instructions for Arch Linux.
Clarified Python version requirements.
```

## Project Structure

```
WIFIjam/
├── wifijam/              # Main package
│   ├── core/            # Core functionality
│   ├── wifi/            # WiFi operations
│   ├── api/             # API server
│   └── cli.py           # CLI interface
├── tests/               # Test suite
├── docs/                # Documentation
├── website/             # Dashboard files
├── Logo/                # Images and logos
├── setup.py             # Package setup
├── requirements.txt     # Dependencies
└── README_NEW.md        # Main documentation
```

## Release Process

1. Update version in `wifijam/__init__.py`
2. Update version in `setup.py`
3. Update CHANGELOG.md
4. Create git tag
5. Push to GitHub
6. Create GitHub release
7. Publish to PyPI (maintainers only)

## Questions?

- Open an issue for questions
- Join discussions on GitHub
- Contact: admin@aryanvbw.live

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WIFIjam! 🎉


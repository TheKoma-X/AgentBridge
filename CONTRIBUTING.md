# Contributing to AgentBridge

Thank you for your interest in contributing to AgentBridge! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Adding New Adapters](#adding-new-adapters)
- [Submitting Changes](#submitting-changes)
- [Code Standards](#code-standards)
- [Testing](#testing)

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/AgentBridge.git`
3. Create a new branch for your feature: `git checkout -b feature/my-feature`

## Development Setup

1. Ensure you have Python 3.8+ installed
2. Install dependencies: `pip install -e ".[dev]"`
3. Install pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Project Structure

```
AgentBridge/
├── agentbridge/           # Main package
│   ├── __init__.py        # Package init
│   ├── bridge.py          # Core bridge logic
│   ├── protocol.py        # Message protocol
│   ├── adapter.py         # Framework adapters
│   ├── server.py          # FastAPI server
│   ├── cli.py             # Command line interface
│   └── utils.py           # Utility functions
├── examples/              # Usage examples
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
├── README.md              # Main documentation
└── CONTRIBUTING.md        # This file
```

## Adding New Adapters

To add support for a new agent framework:

1. Create a new adapter class in `agentbridge/adapter.py` that inherits from `BaseAdapter`
2. Implement all required abstract methods
3. Register your adapter in the `AdapterRegistry` constructor
4. Add tests for your adapter
5. Update documentation

Example adapter:

```python
class MyFrameworkAdapter(BaseAdapter):
    async def send_message(self, message: Any) -> Any:
        # Implementation for your framework
        pass
    
    async def get_capabilities(self) -> Dict[str, Any]:
        # Implementation
        pass
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        # Implementation
        pass
```

## Submitting Changes

1. Ensure all tests pass: `pytest`
2. Update documentation if needed
3. Add tests for new functionality
4. Submit a pull request to the `main` branch

## Code Standards

- Follow PEP 8 style guide
- Use type hints for all public functions
- Write docstrings for all public classes and functions
- Keep functions focused and modular
- Use meaningful variable names

## Testing

- Write unit tests for new functionality
- Use pytest for testing
- Aim for high test coverage
- Test edge cases and error conditions

Run tests with:
```bash
pytest
pytest --cov=agentbridge  # with coverage report
```

## Questions?

If you have any questions, feel free to open an issue or contact the maintainers.

Thank you for contributing to AgentBridge!
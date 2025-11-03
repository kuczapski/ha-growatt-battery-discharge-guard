# Home Assistant Battery Management Plugin

This workspace contains a Home Assistant custom component plugin for battery management.

## Project Structure
- `/custom_components/battery_management/` - Main plugin code
  - `__init__.py` - Integration setup and entry points
  - `config_flow.py` - Configuration flow for UI setup
  - `const.py` - Constants and configuration values
  - `manifest.json` - Integration metadata and requirements
  - `sensor.py` - Battery level and charging status sensors
  - `switch.py` - Battery management control switches
- `/tests/` - Unit tests with comprehensive mocking
- `/docs/` - Documentation (README.md, DEVELOPMENT.md)
- `setup.py` - Python package configuration
- `requirements.txt` - Runtime dependencies
- `pyproject.toml` - Development tool configuration

## Development Guidelines
- Follow Home Assistant development standards
- Use type hints in all Python code
- Write unit tests for all new functionality
- Update documentation for API changes
- Follow semantic versioning

## Available VS Code Tasks
- **Run Tests**: Execute pytest with comprehensive test coverage
- **Format Code**: Auto-format with Black
- **Lint Code**: Check code quality with Pylint
- **Type Check**: Run MyPy type checking
- **Install Dependencies**: Install runtime and dev dependencies

## Testing
- Run `pytest` for unit tests (or use VS Code task)
- Use Home Assistant test environment for integration testing
- Test with multiple Home Assistant versions
- All tests currently pass with mock Home Assistant environment

## Coding Standards
- Use Black for code formatting
- Use pylint for linting
- Follow Home Assistant's coding standards
- Use async/await patterns for I/O operations

## Development Environment
- Python 3.14 configured
- All dependencies installed
- VS Code tasks configured for development workflow
- Comprehensive test mocking for Home Assistant components
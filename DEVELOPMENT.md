# Development Guide

## Quick Start

Your Home Assistant Battery Management plugin is ready for development! Here's how to get started:

### Running Tests
```bash
# Run all tests
C:/Users/ARK/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest -v

# Or use VS Code task: Ctrl+Shift+P → "Tasks: Run Task" → "Run Tests"
```

### Code Quality Tools
```bash
# Format code
C:/Users/ARK/AppData/Local/Python/pythoncore-3.14-64/python.exe -m black custom_components/ tests/

# Lint code
C:/Users/ARK/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pylint custom_components/battery_management/

# Type checking
C:/Users/ARK/AppData/Local/Python/pythoncore-3.14-64/python.exe -m mypy custom_components/battery_management/
```

### Testing in Home Assistant

1. **Copy to Home Assistant**: Copy the `custom_components/battery_management` folder to your Home Assistant's `custom_components` directory
2. **Restart Home Assistant**: Restart your Home Assistant instance
3. **Add Integration**: Go to Settings → Devices & Services → Add Integration → Search "Battery Management"

### Development Workflow

1. **Make changes** to the code in `custom_components/battery_management/`
2. **Run tests** to ensure functionality: VS Code task "Run Tests" 
3. **Format code** with Black: VS Code task "Format Code"
4. **Check linting** with Pylint: VS Code task "Lint Code"
5. **Test in Home Assistant** by copying the updated component

### VS Code Tasks Available

- **Run Tests**: Execute all pytest tests
- **Format Code**: Auto-format with Black
- **Lint Code**: Check code quality with Pylint
- **Type Check**: Run MyPy type checking
- **Install Dependencies**: Install runtime dependencies
- **Install Dev Dependencies**: Install development dependencies

### Project Structure

```
custom_components/battery_management/
├── __init__.py          # Integration setup
├── config_flow.py       # Configuration UI
├── const.py            # Constants
├── manifest.json       # Integration metadata
├── sensor.py           # Battery sensors
└── switch.py           # Control switches
```

### Next Steps

1. Customize the battery monitoring logic in `sensor.py`
2. Add actual hardware integration
3. Extend functionality in `switch.py`
4. Add more comprehensive tests
5. Update documentation as needed
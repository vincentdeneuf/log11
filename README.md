# log11

A modern, flexible Python logging library designed for simplicity and power.

## Features

- **Modern API**: Built on top of the powerful loguru library
- **Flexible Configuration**: Multiple output formats (text/JSON)
- **Rich Formatting**: Colored output, custom fields, and structured logging
- **Project Root Detection**: Automatic project root discovery
- **Python 3.10+**: Modern Python features and type hints
- **Zero Configuration**: Sensible defaults out of the box

## Installation

```bash
pip install log11
```

## Quick Start

### Basic Usage

```python
from log11 import get_logger

# Get the default logger
logger = get_logger()

# Log messages
logger.info("Application started")
logger.warning("This is a warning")
logger.error("Something went wrong")
```

### Advanced Usage

```python
from log11 import Log, TextFormatConfig

# Setup custom logging configuration
Log.clear()
Log.add_output(
    name="console",
    sink="logs/app.log",
    data_format="json",
    level="INFO",
    text_format_config=TextFormatConfig(
        date=True,
        time=True,
        level=True,
        location=False,
        function=True,
        message=True,
        extras=True
    )
)

# Apply configuration and get logger
logger = Log.apply()

# Log structured data
logger.info("User action", user_id=123, action="login")
```

### Custom Formatting

```python
from log11 import Log, TextFormatConfig, LogColor

# Setup with custom formatting
Log.clear()
Log.add_output(
    name="console",
    sink="stdout",
    data_format="text",
    colored=True,
    level="DEBUG",
    text_format_config=TextFormatConfig(
        date=False,
        time=True,
        level=True,
        location=True,
        function=False,
        message=True,
        extras=True
    )
)

logger = Log.apply()
logger.debug("Debug message with details", debug_info="extra data")
```

## API Reference

### Log

The main logging configuration manager.

- `Log.clear()`: Clear all output configurations
- `Log.default_setup()`: Setup default console logging
- `Log.apply()`: Apply all configured outputs and return logger
- `Log.add_output(name, sink, data_format, colored, level, text_format_config, replace, auto_apply, **kwargs)`: Add a new output configuration
- `Log.add_level(name, number, color)`: Add a custom logging level
- `Log.set_global_level(level)`: Set logging level for all outputs

### get_logger

- `get_logger()`: Get a configured logger instance (sets up defaults if needed)

### Configuration Classes

- `TextFormatConfig(date, time, level, location, function, message, extras)`: Configure text output format
- `TextFormat(config)`: Text formatter implementation
- `LogColor`: Color constants for styling
- `LogStyle`: Text styling helpers
- `LogField`: Field rendering utilities

## Development

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) for modern Python dependency management:

```bash
# On Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/vincentdeneuf/log11.git
cd log11

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment (optional, uv commands work without it)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

### Running Tests

```bash
# Run tests with uv
uv run pytest

# Run tests with coverage
uv run pytest --cov=log11 --cov-report=html
```

### Building the Package

```bash
# Build the package
uv build

# Build for distribution
uv build --release
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0
- Initial release
- Built on loguru for powerful logging capabilities
- Flexible output configuration (text/JSON formats)
- Rich formatting with colors and custom fields
- Project root detection
- Python 3.10+ support with modern type hints
- Zero-configuration default setup
# log11

A simple logging library built on top of loguru.

## Installation

```bash
pip install log11
```

## Quick Start

```python
from log11 import get_logger

# Get the default logger
logger = get_logger()

# Log messages
logger.info("Application started")
logger.warning("This is a warning")
logger.error("Something went wrong")
```

## Advanced Configuration

### Different Output Formats and Sinks

```python
from log11 import Log, TextFormatConfig
import sys

# Clear any existing configuration
Log.clear()

# 1. JSON output to file
Log.add_output(
    name="file_json",
    sink="logs/app.log",
    data_format="json",
    level="INFO"
)

# 2. Plain text output to file
Log.add_output(
    name="file_text",
    sink="logs/app.txt", 
    data_format="text",
    colored=False,
    level="DEBUG"
)

# 3. Colored text output to console
Log.add_output(
    name="console_colored",
    sink=sys.stdout,
    data_format="text",
    colored=True,
    level="INFO",
    text_format_config=TextFormatConfig(
        date=False,
        time=True,
        level=True,
        location=True,
        function=True,
        message=True,
        extras=True
    )
)

# Get logger with all outputs configured
logger = get_logger()

# Log messages - they'll appear in all configured outputs
logger.info("User logged in", user_id=123, username="alice")
logger.debug("Debug information", debug_data={"key": "value"})
```

### Environment-Specific Configuration

```python
from log11 import Log, TextFormatConfig
import sys
import os

# Clear any existing configuration
Log.clear()

if os.getenv("ENV") == "production":
    # Production: JSON to file only
    Log.add_output(
        name="production",
        sink="logs/production.log",
        data_format="json",
        level="INFO"
    )
else:
    # Development: Colored text to console
    Log.add_output(
        name="development",
        sink=sys.stdout,
        data_format="text", 
        colored=True,
        level="DEBUG",
        text_format_config=TextFormatConfig(
            date=False,
            time=True,
            level=True,
            location=True,
            function=True,
            message=True,
            extras=True
        )
    )

logger = get_logger()
logger.info("Environment-specific logging")

## API Reference

### Log

The main logging configuration manager.

- `Log.clear()`: Clear all output configurations
- `Log.default_setup()`: Setup default console logging
- `Log.add_output(name, sink, data_format, colored, level, text_format_config, **kwargs)`: Add a new output configuration
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

"""
log11 - A Python logging library

A modern, flexible logging library for Python applications built on loguru.
"""

__version__ = "0.1.0"
__author__ = "vincentdeneuf"
__email__ = "your.email@example.com"

from .main import (
    Log,
    LogColor,
    LogField,
    LogStyle,
    TextFormat,
    TextFormatConfig,
    get_logger,
)

__all__ = [
    "Log",
    "LogColor",
    "LogStyle",
    "LogField",
    "TextFormatConfig",
    "TextFormat",
    "get_logger",
]

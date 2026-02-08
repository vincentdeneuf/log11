import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from log11.main import Log, get_logger, DEFAULT_LOG_LEVEL


class TestLoggingCapacity:
    """Test suite for basic logging capacity and functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        Log.clear()

    def teardown_method(self):
        """Clean up after each test."""
        Log.clear()

    def test_get_logger(self):
        """Test getting logger instance."""
        # Test getting logger without setup
        logger = get_logger()
        assert logger is not None
        
        # Test getting logger after setup
        Log.clear()
        logger = get_logger()
        assert logger is not None
        assert Log._outputs

    def test_add_custom_level(self):
        """Test adding a custom log level."""
        # Add a custom level
        Log.add_level(
            name="CUSTOM",
            number=35,
            color="cyan"
        )
        
        # Verify the level was added
        from loguru import logger
        assert "CUSTOM" in {level.name for level in logger._core.levels.values()}
        
        # Verify the method was added
        assert hasattr(logger, "custom")
        
        # Test using the custom level
        Log.add_output(
            name="test",
            sink=sys.stdout,
            level="CUSTOM"
        )
        
        # This should not raise an exception
        logger.custom("Test custom level message")

    def test_all_log_levels_console(self):
        """Test all log levels work in console output."""
        # Add console output with lowest level to capture all
        Log.add_output(
            name="console",
            sink=sys.stdout,
            level="TRACE",  # Lowest level to capture everything
            colored=True
        )
        
        from loguru import logger
        
        # Test all standard levels
        test_messages = {
            "trace": "Trace message",
            "debug": "Debug message", 
            "info": "Info message",
            "success": "Success message",
            "warning": "Warning message",
            "error": "Error message",
            "critical": "Critical message"
        }
        
        # Capture output to verify it works
        with patch('sys.stdout') as mock_stdout:
            for level, message in test_messages.items():
                getattr(logger, level)(message)
            
            # Verify that write was called for each message
            assert mock_stdout.write.call_count >= len(test_messages)

    def test_all_log_levels_file(self):
        """Test all log levels work in file output."""
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Add file output
            Log.add_output(
                name="file",
                sink=temp_path,
                level="TRACE",  # Lowest level to capture everything
                colored=False
            )
            
            from loguru import logger
            
            # Test all standard levels
            test_messages = [
                ("trace", "Trace message"),
                ("debug", "Debug message"),
                ("info", "Info message"),
                ("success", "Success message"),
                ("warning", "Warning message"),
                ("error", "Error message"),
                ("critical", "Critical message")
            ]
            
            # Log all messages
            for level, message in test_messages:
                getattr(logger, level)(message)
            
            # Force flush
            logger.remove()
            
            # Read file and verify all messages were written
            with open(temp_path, 'r') as f:
                content = f.read()
                
            for level, message in test_messages:
                assert message in content
                assert level.upper() in content
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_extra_functionality(self):
        """Test that extra parameters work correctly."""
        # Add console output
        Log.add_output(
            name="console",
            sink=sys.stdout,
            level="INFO",
            colored=True
        )
        
        from loguru import logger
        
        # Test logging with extra parameters
        with patch('sys.stdout') as mock_stdout:
            logger.info(
                "Test message with extras",
                user_id=123,
                action="test_action",
                data={"key": "value"}
            )
            
            # Verify output contains extra information
            mock_stdout.write.assert_called()
            output_calls = [call[0][0] for call in mock_stdout.write.call_args_list]
            output_text = ''.join(output_calls)
            
            # Should contain the extra fields
            assert "user_id=123" in output_text
            assert "action=test_action" in output_text
            assert "data={'key': 'value'}" in output_text

    def test_combined_functionality(self):
        """Test all functionality working together."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Set up complete logging configuration
            Log.add_level(
                name="TEST",
                number=25,
                color="magenta"
            )
            
            Log.add_output(
                name="console",
                sink=sys.stdout,
                level="DEBUG",
                colored=True
            )
            
            Log.add_output(
                name="file",
                sink=temp_path,
                level="DEBUG",
                colored=False
            )
            
            from loguru import logger
            
            # Test all functionality together
            with patch('sys.stdout') as mock_stdout:
                # Standard levels
                logger.debug("Debug message")
                logger.info("Info message")
                logger.warning("Warning message")
                
                # Custom level
                logger.test("Custom test message")
                
                # With extras
                logger.error(
                    "Error with context",
                    error_code=500,
                    user="test_user"
                )
                
                # Verify console output
                assert mock_stdout.write.call_count > 0
            
            # Force flush and verify file output
            logger.remove()
            
            with open(temp_path, 'r') as f:
                content = f.read()
                
            # Verify all messages are in file
            assert "Debug message" in content
            assert "Info message" in content
            assert "Warning message" in content
            assert "Custom test message" in content
            assert "Error with context" in content
            assert "error_code=500" in content
            assert "user=test_user" in content
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_default_setup(self):
        """Test the default setup functionality."""
        # Test default setup
        logger = Log.default_setup()
        
        assert logger is not None
        assert "default" in Log._outputs
        assert Log._outputs["default"].level == DEFAULT_LOG_LEVEL
        
        # Test that custom level was added
        from loguru import logger as loguru_logger
        assert "TEMP" in {level.name for level in loguru_logger._core.levels.values()}
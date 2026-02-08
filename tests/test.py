from pathlib import Path
import json
import math
import tempfile

from log11 import (
    get_logger,
    Log,
    LogColor,
    TextFormatConfig,
)


def test_default_logger():
    print("\n--- test_default_logger ---")

    Log.clear()
    logger = get_logger()
    logger.info("hello world")

    assert Log._outputs, "Expected default outputs to be configured"
    assert "default" in Log._outputs

    print("test_default_logger passed")


def test_extras_rendering():
    print("\n--- test_extras_rendering ---")

    Log.clear()
    logger = get_logger()

    logger.info(
        "user login",
        user_id=123,
        active=True,
        score=12.5,
        nothing=None,
    )

    # If formatting or patching fails, logging would raise
    assert True

    print("test_extras_rendering passed")


def test_file_output_text():
    print("\n--- test_file_output_text ---")

    with tempfile.TemporaryDirectory() as tmp:
        log_file = Path(tmp) / "app.log"

        Log.clear()
        Log.add_output(
            name="file",
            sink=log_file,
            data_format="text",
            colored=False,
            level="INFO",
            text_format_config=TextFormatConfig(
                date=False,
                time=False,
                location=False,
                function=False,
            ),
        )

        logger = get_logger()
        logger.info(
            "file message",
            value=42,
            empty="",
            nan_value=math.nan,
        )

        content = log_file.read_text()
        print(content)

        assert "file message" in content
        assert "value=42" in content
        assert "empty=_EMPTY_" in content
        assert "nan_value=_NAN_" in content

        # ✅ Release file handle before temp cleanup (Windows)
        Log.clear()

    print("test_file_output_text passed")

def test_json_output():
    print("\n--- test_json_output ---")

    with tempfile.TemporaryDirectory() as tmp:
        log_file = Path(tmp) / "app.json.log"

        Log.clear()
        Log.add_output(
            name="json",
            sink=log_file,
            data_format="json",
            level="INFO",
        )

        logger = get_logger()
        logger.info(
            "json message",
            count=3,
            ok=True,
            nothing=None,
        )

        # ✅ Close handlers so file is flushed and unlocked
        Log.clear()

        raw = log_file.read_bytes().decode("utf-8").strip()
        payload = json.loads(raw)

        print(payload)

        record = payload["record"]

        assert record["message"] == "json message"
        assert record["extra"]["count"] == "3"
        assert record["extra"]["ok"] == "True"
        assert record["extra"]["nothing"] == "_NULL_"

    print("test_json_output passed")

def test_custom_level():
    print("\n--- test_custom_level ---")

    Log.clear()
    Log.add_level("TEMP", 25, LogColor.MAGENTA)

    logger = get_logger()
    logger.temp("temporary message")

    levels = {level.name for level in logger._core.levels.values()}
    assert "TEMP" in levels

    print("test_custom_level passed")


if __name__ == "__main__":
    print("\n=== log11 example tests ===")

    test_default_logger()
    test_extras_rendering()
    test_file_output_text()
    test_json_output()
    test_custom_level()

    print("\n✅ All log11 tests passed")
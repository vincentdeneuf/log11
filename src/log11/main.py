import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Union, Optional, Dict, Any

from loguru import logger

DEFAULT_LOG_LEVEL: str = "INFO"
STRING_MAX_LENGTH = 100

DataFormatType = Literal["text", "json"]
LevelType = Union[int, str]


def find_project_root(start_path: Path) -> Path:
    """Find project root by locating pyproject.toml or .git directory."""
    current: Path = start_path.resolve()

    for parent in (current, *current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".git").exists():
            return parent

    return current


PROJECT_ROOT: Path = find_project_root(Path(__file__))


def to_string(value: any, max_length: int = STRING_MAX_LENGTH) -> str:
    """Safely convert any value to a truncated string suitable for logging."""
    if value is None:
        return "<NULL>"

    if value == "":
        return "<EMPTY>"

    if isinstance(value, float):
        if math.isnan(value):
            return "<NAN>"
        if math.isinf(value):
            return "<INFINITY>" if value > 0 else "<-INFINITY>"

    try:
        if hasattr(value, "model_dump") and callable(value.model_dump):
            text = repr(value.model_dump())
        elif hasattr(value, "dict") and callable(value.dict):
            text = repr(value.dict())
        else:
            text = repr(value)
    except Exception:
        try:
            text = str(value)
        except Exception:
            text = f"<UNPRINTABLE {type(value).__name__}>"

    if len(text) > max_length:
        text = text[: max_length - 3] + "..."

    return text


class LogColor:
    """Named colors compatible with Loguru."""

    BLACK: str = "black"
    RED: str = "red"
    GREEN: str = "green"
    YELLOW: str = "yellow"
    BLUE: str = "blue"
    MAGENTA: str = "magenta"
    CYAN: str = "cyan"
    WHITE: str = "white"

    LIGHT_BLACK: str = "light-black"
    LIGHT_RED: str = "light-red"
    LIGHT_GREEN: str = "light-green"
    LIGHT_BLUE: str = "light-blue"

    LEVEL: str = "level"


LEVEL_TEMP: dict[str, any] = {
    "name": "TEMP",
    "number": 25,
    "color": LogColor.MAGENTA,
}


class LogStyle:
    """Text styling helpers for Loguru."""

    @staticmethod
    def apply(
        value: str,
        color: Optional[str] = None,
        *,
        dim: bool = False,
        bold: bool = False,
        width: Optional[int] = None,
    ) -> str:
        text: str = value

        if width is not None:
            text = f"{text:<{width}}"

        if color:
            text = f"<{color}>{text}</{color}>"

        if dim:
            text = f"<dim>{text}</dim>"

        if bold:
            text = f"<bold>{text}</bold>"

        return text


class LogField:
    """Atomic log field renderers."""

    @staticmethod
    def render_date(record: dict[str, any]) -> str:
        return LogStyle.apply(
            record["time"].strftime("%Y-%m-%d"),
            dim=True,
        )

    @staticmethod
    def render_time(record: dict[str, any]) -> str:
        return LogStyle.apply(
            record["time"].strftime("%H:%M:%S"),
            dim=True,
        )

    @staticmethod
    def render_level(record: dict[str, any]) -> str:
        level_name: str = record["level"].name

        return LogStyle.apply(
            level_name,
            color=LogColor.LEVEL,
            bold=True,
            width=Log._level_width,
        )

    @staticmethod
    def render_location(record: dict[str, any]) -> str:
        path: Path = Path(record["file"].path)

        try:
            path = path.relative_to(PROJECT_ROOT)
        except ValueError:
            pass

        location: str = f"{path}:{record['line']}"

        return LogStyle.apply(location)

    @staticmethod
    def render_function(record: dict[str, any]) -> str:
        name: str = record["function"]

        if name == "<module>":
            return "__"

        if name.startswith("<") and name.endswith(">"):
            name = name[1:-1]

        return f"{name}()"

    @staticmethod
    def render_message(record: dict[str, any]) -> str:
        return LogStyle.apply(record["message"], bold=True)

    @staticmethod
    def render_extras(record: dict[str, any]) -> str:
        extras: dict[str, any] = record["extra"]

        if not extras:
            return ""

        parts: list[str] = []

        for key, value in extras.items():
            key_text: str = LogStyle.apply(key, color=LogColor.GREEN)
            value_text: str = to_string(value)
            parts.append(f"{key_text}={value_text}")

        return " | ".join(parts)


@dataclass(frozen=True)
class TextFormatConfig:
    date: bool = True
    time: bool = True
    level: bool = True
    location: bool = True
    function: bool = True
    message: bool = True
    extras: bool = True


class TextFormat:
    """Text formatter for log records."""

    def __init__(self, config: TextFormatConfig) -> None:
        self.config = config

    def render(self, record: dict[str, any]) -> str:
        parts: list[str] = []

        if self.config.date:
            parts.append(LogField.render_date(record))

        if self.config.time:
            parts.append(LogField.render_time(record))

        if self.config.level:
            parts.append(LogField.render_level(record))

        if self.config.location:
            parts.append(LogField.render_location(record))

        if self.config.function:
            parts.append(LogField.render_function(record))

        if self.config.message:
            parts.append(LogField.render_message(record))

        if self.config.extras:
            extras: str = LogField.render_extras(record)
            if extras:
                parts.append(extras)

        return "  ".join(parts) + "\n"


class OutputConfig:
    """Internal output configuration container."""

    def __init__(
        self,
        *,
        sink: any,
        data_format: DataFormatType,
        colored: bool,
        level: LevelType,
        text_format: Optional[TextFormat],
        kwargs: Dict[str, Any],
    ) -> None:
        self.sink = sink
        self.data_format = data_format
        self.colored = colored
        self.level = level
        self.text_format = text_format
        self.kwargs = kwargs


class Log:
    """Central logging configuration manager."""

    _level_width: int = 8
    _outputs: dict[str, OutputConfig] = {}

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _calculate_level_width(cls) -> None:
        cls._level_width = max(
            len(level.name)
            for level in logger._core.levels.values()
        )

    @classmethod
    def _build_output(cls, config: OutputConfig) -> None:
        if config.data_format == "json":
            logger.add(
                config.sink,
                serialize=True,
                level=config.level,
                enqueue=True,
                **config.kwargs,
            )
            return

        text_format = config.text_format or TextFormat(TextFormatConfig())

        logger.add(
            config.sink,
            format=text_format.render,
            colorize=config.colored,
            level=config.level,
            enqueue=True,
            **config.kwargs,
        )

    @classmethod
    def _rebuild_outputs(cls) -> None:
        logger.remove()

        for config in cls._outputs.values():
            cls._build_output(config)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    @classmethod
    def default_setup(cls):
        cls.clear()

        cls.add_output(
            name="default",
            sink=sys.stdout,
            data_format="text",
            colored=True,
            level=DEFAULT_LOG_LEVEL,
            text_format_config=TextFormatConfig(date=False),
        )

        return logger

    @classmethod
    def clear(cls) -> None:
        cls._outputs.clear()
        logger.remove()

    @classmethod
    def add_output(
        cls,
        *,
        name: str,
        sink: Any,
        data_format: DataFormatType = "text",
        colored: bool = False,
        level: LevelType = DEFAULT_LOG_LEVEL,
        text_format_config: Optional[TextFormatConfig] = None,
        **kwargs: Any,
    ) -> None:
        if name in cls._outputs:
            raise ValueError(
                f"Log output '{name}' already exists."
            )

        text_format = (
            TextFormat(text_format_config)
            if text_format_config is not None
            else None
        )

        cls._outputs[name] = OutputConfig(
            sink=sink,
            data_format=data_format,
            colored=colored,
            level=level,
            text_format=text_format,
            kwargs=kwargs,
        )

        cls._rebuild_outputs()

    @classmethod
    def set_global_level(cls, level: LevelType) -> None:
        for config in cls._outputs.values():
            config.level = level

        cls._rebuild_outputs()

    @classmethod
    def add_level(
        cls,
        name: str,
        number: int,
        color: str | None = None,
    ) -> None:
        level_name = name.upper()

        existing_levels = {
            level.name for level in logger._core.levels.values()
        }

        if level_name not in existing_levels:
            logger.level(
                level_name,
                no=number,
                color=f"<{color}>" if color else None,
            )

        method_name = name.lower()

        if not hasattr(logger, method_name):

            def log_method(message: str, **kwargs: any) -> None:
                logger.opt(depth=1).log(level_name, message, **kwargs)

            setattr(logger, method_name, log_method)

        cls._calculate_level_width()
        cls._rebuild_outputs()


def get_logger():
    """Default public logger accessor."""
    if not Log._outputs:
        return Log.default_setup()

    return logger
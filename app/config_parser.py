import os
from dataclasses import dataclass
from typing import Optional

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
OPTIONAL_KEYS = ("SEED",)


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


@dataclass
class Config:
    """Validated configuration values."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _read_pairs(path: str) -> dict[str, str]:
    """Read KEY=VALUE pairs from the file, skipping comments and blanks."""
    pairs: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            for number, raw in enumerate(file, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"line {number}: expected KEY=VALUE, got '{line}'")
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()
                if key not in MANDATORY_KEYS + OPTIONAL_KEYS:
                    raise ConfigError(f"line {number}: unknown key '{key}'")
                if key in pairs:
                    raise ConfigError(f"line {number}: duplicate key '{key}'")
                if not value:
                    raise ConfigError(f"line {number}: empty value for '{key}'")
                pairs[key] = value
    except FileNotFoundError:
        raise ConfigError(f"config file '{path}' not found") from None
    except PermissionError:
        raise ConfigError(f"no permission to read '{path}'") from None
    except IsADirectoryError:
        raise ConfigError(f"'{path}' is a directory, not a file") from None
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' is not a valid text file") from None
    except OSError as err:
        raise ConfigError(f"cannot read '{path}': {err.strerror}") from None
    return pairs


def _parse_int(key: str, value: str) -> int:
    """Convert a value to int or raise a clear ConfigError."""
    try:
        return int(value)
    except ValueError:
        raise ConfigError(f"{key}: '{value}' is not an integer") from None


def _parse_positive(key: str, value: str) -> int:
    """Convert a value to a strictly positive int."""
    number = _parse_int(key, value)
    if number <= 0:
        raise ConfigError(f"{key}: must be greater than 0, got {number}")
    return number


def _parse_coords(key: str, value: str) -> tuple[int, int]:
    """Convert 'x,y' to a tuple of ints."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key}: expected format x,y, got '{value}'")
    return (_parse_int(key, parts[0].strip()),
            _parse_int(key, parts[1].strip()))


def _parse_bool(key: str, value: str) -> bool:
    """Convert 'True'/'False' (any case) to bool."""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key}: expected True or False, got '{value}'")


def _check_in_bounds(key: str, point: tuple[int, int],
                     width: int, height: int) -> None:
    """Ensure a coordinate pair lies inside the maze."""
    x, y = point
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"{key}: {x},{y} is outside the maze "
            f"(valid: 0-{width - 1}, 0-{height - 1})")


def _check_output_writable(path: str) -> None:
    """Ensure the output file can be created or overwritten."""
    if os.path.isdir(path):
        raise ConfigError(f"OUTPUT_FILE: '{path}' is a directory")
    folder = os.path.dirname(path) or "."
    if not os.path.isdir(folder):
        raise ConfigError(f"OUTPUT_FILE: folder '{folder}' does not exist")
    if os.path.exists(path):
        if not os.access(path, os.W_OK):
            raise ConfigError(f"OUTPUT_FILE: '{path}' is not writable")
    elif not os.access(folder, os.W_OK):
        raise ConfigError(f"OUTPUT_FILE: cannot write in '{folder}'")


def parse_config(path: str) -> Config:
    """Read and validate the config file, returning a Config object.

    Raises:
        ConfigError: with a human-readable message on any problem.
    """
    pairs = _read_pairs(path)

    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")

    width = _parse_positive("WIDTH", pairs["WIDTH"])
    height = _parse_positive("HEIGHT", pairs["HEIGHT"])
    entry = _parse_coords("ENTRY", pairs["ENTRY"])
    exit_ = _parse_coords("EXIT", pairs["EXIT"])
    perfect = _parse_bool("PERFECT", pairs["PERFECT"])
    output_file = pairs["OUTPUT_FILE"]

    _check_in_bounds("ENTRY", entry, width, height)
    _check_in_bounds("EXIT", exit_, width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different")
    _check_output_writable(output_file)

    seed: Optional[int] = None
    if "SEED" in pairs:
        seed = _parse_int("SEED", pairs["SEED"])

    return Config(width, height, entry, exit_, output_file, perfect, seed)
class OutputError(Exception):
    """Raised when the maze cannot be written to the output file."""


def format_maze(grid: list[list[int]], entry: tuple[int, int],
                exit: tuple[int, int], solution: list[str]) -> str:
    """Build the full text content of the output file."""
    lines: list[str] = []
    for row in grid:
        for cell in row:
            if not 0 <= cell <= 15:
                raise OutputError(f"invalid cell value: {cell}")
        lines.append("".join(f"{cell:X}" for cell in row))
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit[0]},{exit[1]}")
    lines.append("".join(solution))
    return "\n".join(lines) + "\n"


def write_maze(path: str, grid: list[list[int]], entry: tuple[int, int],
               exit: tuple[int, int], solution: list[str]) -> None:
    """Write the maze to ``path``.

    Raises:
        OutputError: if the file cannot be written.
    """
    content = format_maze(grid, entry, exit, solution)
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as file:
            file.write(content)
    except OSError as err:
        raise OutputError(
            f"cannot write '{path}': {err.strerror}") from None

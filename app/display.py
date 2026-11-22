from typing import Callable, Protocol

# Wall bits: 1 = closed wall
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

# Solution letter -> (dx, dy)
STEPS: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

# ANSI background colors
RESET = "\033[0m"
WALL_COLORS = ["47", "44", "46", "45"]
ENTRY_COLOR = "42"
EXIT_COLOR = "41"
PATH_COLOR = "43"
PATTERN_COLOR = "48;5;208"

MENU = """
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show/Hide path
3. Change wall color
4. Quit
"""


class MazeLike(Protocol):
    """What the display needs from the maze generator (the contract)."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    grid: list[list[int]]
    solution: list[str]
    pattern_cells: set[tuple[int, int]]


def build_canvas(maze: MazeLike, show_path: bool) -> list[list[str]]:
    """Convert the maze into a canvas of symbols.

    Symbols: 'W' wall, ' ' open, 'S' entry, 'X' exit, 'P' path,
    'F' cell of the "42" pattern.
    """
    canvas = [["W"] * (2 * maze.width + 1) for _ in range(2 * maze.height + 1)]
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]
            cy, cx = 2 * y + 1, 2 * x + 1
            canvas[cy][cx] = " "
            if not cell & NORTH:
                canvas[cy - 1][cx] = " "
            if not cell & EAST:
                canvas[cy][cx + 1] = " "
            if not cell & SOUTH:
                canvas[cy + 1][cx] = " "
            if not cell & WEST:
                canvas[cy][cx - 1] = " "
    for x, y in maze.pattern_cells:
        canvas[2 * y + 1][2 * x + 1] = "F"
    if show_path:
        x, y = maze.entry
        for letter in maze.solution:
            dx, dy = STEPS[letter]
            canvas[2 * y + 1 + dy][2 * x + 1 + dx] = "P"
            x, y = x + dx, y + dy
            canvas[2 * y + 1][2 * x + 1] = "P"
    canvas[2 * maze.entry[1] + 1][2 * maze.entry[0] + 1] = "S"
    canvas[2 * maze.exit[1] + 1][2 * maze.exit[0] + 1] = "X"
    return canvas


def render(maze: MazeLike, show_path: bool, wall_color: str) -> str:
    """Return the colored text drawing of the maze."""
    colors = {
        "W": wall_color,
        "S": ENTRY_COLOR,
        "X": EXIT_COLOR,
        "P": PATH_COLOR,
        "F": PATTERN_COLOR,
    }
    labels = {"S": "ST", "X": "EX"}
    lines: list[str] = []
    for row in build_canvas(maze, show_path):
        parts: list[str] = []
        for symbol in row:
            if symbol == " ":
                parts.append("  ")
            else:
                label = labels.get(symbol, "  ")
                parts.append(f"\033[{colors[symbol]}m{label}{RESET}")
        lines.append("".join(parts))
    return "\n".join(lines)


def run_display(maze: MazeLike,
                regenerate: Callable[[], MazeLike]) -> None:
    """Show the maze and run the interactive menu until the user quits."""
    show_path = False
    color_index = 0
    while True:
        print(render(maze, show_path, WALL_COLORS[color_index]))
        print(MENU)
        try:
            choice = input("Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == "1":
            maze = regenerate()
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
        elif choice == "4":
            return
        else:
            print("Invalid choice, enter a number from 1 to 4.")

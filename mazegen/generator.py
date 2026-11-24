import random
from collections import deque
WALL_BITS: dict[str, int] = {"N": 1, "E": 2, "S": 4, "W": 8}
WALL_OPPOSITE: dict[str, str] = {"N": "S", "E": "W", "S": "N", "W": "E"}
MOVES: dict[str, tuple[int, int]] = {
    "N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)
}
FOUR: list[str] = ["#.#", "#.#", "###", "..#", "..#"]
TWO: list[str] = ["###", "..#", "###", "#..", "###"]


def create_closed_grid(width: int, height: int) -> list[list[int]]:
    """the function takes 2 parameters and creates a grid from
        that and return the list of ints that makes the grid"""
    return [[15 for _ in range(width)] for _ in range(height)]


def open_wall(grid: list[list[int]], x: int, y: int, direction: str) -> None:
    """Opens the wall between a cell and its neighbour"""
    dx, dy = MOVES[direction]
    nx = x + dx
    ny = y + dy
    grid[y][x] &= ~WALL_BITS[direction]
    opposite = WALL_OPPOSITE[direction]
    grid[ny][nx] &= ~WALL_BITS[opposite]


def carve_maze(
        grid: list[list[int]],
        width: int, height: int,
        rng: random.Random,
        blocked: set[tuple[int, int]],
        start: tuple[int, int]
        ) -> None:
    """Carve a perfect maze with a DFS, skipping the blocked cells."""
    x0, y0 = start
    visited: list[list[bool]] = [
        [False for _ in range(width)] for _ in range(height)
        ]
    for bx, by in blocked:
        visited[by][bx] = True
    visited[y0][x0] = True
    stack: list[tuple[int, int]] = [start]
    while stack:
        x, y = stack[-1]
        neighbours: list[tuple[str, int, int]] = []
        for direction in MOVES:
            dx, dy = MOVES[direction]
            nx = x + dx
            ny = y + dy
            in_bounds = 0 <= nx < width and 0 <= ny < height
            if in_bounds and not visited[ny][nx]:
                neighbours.append((direction, nx, ny))
        if neighbours:
            direction, nx, ny = rng.choice(neighbours)
            open_wall(grid, x, y, direction)
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()


def find_path(
        grid: list[list[int]], entry: tuple[int, int],
        exit_: tuple[int, int]
        ) -> list[str]:
    """finds the path to the end and returns the directions"""
    queue = deque([entry])
    came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    height: int = len(grid)
    width: int = len(grid[0])
    while queue:
        x, y = queue.popleft()
        if (x, y) == exit_:
            break
        for direction in MOVES:
            dx, dy = MOVES[direction]
            nx = x + dx
            ny = y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and not grid[y][x] & WALL_BITS[direction]
                and (nx, ny) not in came_from
            ):
                came_from[(nx, ny)] = ((x, y), direction)
                queue.append((nx, ny))
    if exit_ not in came_from:
        return []
    path: list[str] = []
    current: tuple[int, int] = exit_
    while current != entry:
        previous, direction = came_from[current]
        path.append(direction)
        current = previous
    path.reverse()
    return path


def get_pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the cells that draw the 42 pattern"""
    if width < 9 or height < 7:
        print("Maze too small to display the 42 pattern.")
        return set()
    start_x: int = (width - 7) // 2
    start_y: int = (height - 5) // 2
    cells: set[tuple[int, int]] = set()
    for row_index, line in enumerate(FOUR):
        for col_index, char in enumerate(line):
            if char == "#":
                cells.add((start_x + col_index, start_y + row_index))
    for row_index, line in enumerate(TWO):
        for col_index, char in enumerate(line):
            if char == "#":
                cells.add((start_x + 4 + col_index, start_y + row_index))
    return cells


def has_open_3x3(grid: list[list[int]]) -> bool:
    """Return True if the grid has a fully open 3x3 area."""
    height = len(grid)
    width = len(grid[0])
    for y in range(height - 2):
        for x in range(width - 2):
            all_open = True
            for dy in range(3):
                for dx in range(3):
                    if dx < 2 and grid[y + dy][x + dx] & WALL_BITS["E"]:
                        all_open = False
                    if dy < 2 and grid[y + dy][x + dx] & WALL_BITS["S"]:
                        all_open = False
            if all_open:
                return True
    return False


def find_dead_ends(grid: list[list[int]]) -> list[tuple[int, int]]:
    """Return the coordinates of all dead-end cells."""
    dead_ends: list[tuple[int, int]] = []
    height = len(grid)
    width = len(grid[0])
    for y in range(height):
        for x in range(width):
            walls = bin(grid[y][x]).count("1")
            if walls == 3:
                dead_ends.append((x, y))
    return dead_ends


def close_wall(grid: list[list[int]], x: int, y: int, direction: str) -> None:
    """Closes the wall between a cell and its neighbour"""
    dx, dy = MOVES[direction]
    nx = x + dx
    ny = y + dy
    grid[y][x] |= WALL_BITS[direction]
    opposite = WALL_OPPOSITE[direction]
    grid[ny][nx] |= WALL_BITS[opposite]


def braid_dead_ends(
        grid: list[list[int]],
        blocked: set[tuple[int, int]],
        rng: random.Random
        ) -> None:
    """removes the dead ends"""
    height = len(grid)
    width = len(grid[0])
    for x, y in find_dead_ends(grid):
        if bin(grid[y][x]).count("1") != 3:
            continue
        directions = list(MOVES)
        rng.shuffle(directions)
        for direction in directions:
            dx, dy = MOVES[direction]
            nx = x + dx
            ny = y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in blocked:
                continue
            if not grid[y][x] & WALL_BITS[direction]:
                continue
            open_wall(grid, x, y, direction)
            if has_open_3x3(grid):
                close_wall(grid, x, y, direction)
            else:
                break


def has_two_routes(
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_: tuple[int, int]
        ) -> bool:
    """finds a second route independant from the first one"""
    path = find_path(grid, entry, exit_)
    if not path:
        return False
    x, y = entry
    for direction in path:
        close_wall(grid, x, y, direction)
        alternative = find_path(grid, entry, exit_)
        open_wall(grid, x, y, direction)
        if not alternative:
            return False
        dx, dy = MOVES[direction]
        x += dx
        y += dy
    return True


def corners_and_center_open(grid: list[list[int]]) -> bool:
    """Return True if the four corners and the centre are open."""
    height = len(grid)
    width = len(grid[0])
    points: list[tuple[int, int]] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (width // 2, height // 2)
    ]
    for x, y in points:
        walls = bin(grid[y][x]).count("1")
        if walls > 2:
            return False
    return True


class MazeGenerator:
    """Generate a maze and its shortest solution"""
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit_: tuple[int, int],
            perfect: bool = False,
            seed: int | None = None,
    ) -> None:
        if width < 2:
            raise ValueError("width must be at least 2")
        if height < 2:
            raise ValueError("height must be at least 2")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("entry must be inside the grid")
        if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
            raise ValueError("exit must be inside the grid")
        if entry == exit_:
            raise ValueError("entry and exit must be different")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.seed = seed
        self.grid: list[list[int]] = []
        self.solution: list[str] = []
        self.pattern_cells: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate the maze and compute its solution."""
        rng = random.Random(self.seed)
        self.grid = create_closed_grid(self.width, self.height)
        self.pattern_cells = get_pattern_cells(self.width, self.height)
        if self.entry in self.pattern_cells or self.exit in self.pattern_cells:
            raise ValueError(
                "entry and exit must not be inside the 42 pattern")
        carve_maze(
            self.grid,
            self.width,
            self.height,
            rng,
            self.pattern_cells,
            self.entry
        )
        if not self.perfect:
            braid_dead_ends(self.grid, self.pattern_cells, rng)
        self.solution = find_path(self.grid, self.entry, self.exit)

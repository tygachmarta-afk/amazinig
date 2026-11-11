"""A-Maze-ing entry point.

Usage: python3 a_maze_ing.py config.txt
"""

import sys
from typing import Optional

from config_parser import ConfigError, parse_config
from display import run_display
from mazegen import MazeGenerator
from output_writer import OutputError, write_maze


def run(config_path: str) -> None:
    """Parse the config, generate the maze, write it and show it."""
    cfg = parse_config(config_path)

    def build(seed: Optional[int]) -> MazeGenerator:
        """Generate a maze and write it to the output file."""
        gen = MazeGenerator(cfg.width, cfg.height, cfg.entry, cfg.exit,
                            cfg.perfect, seed)
        gen.generate()
        write_maze(cfg.output_file, gen.grid, cfg.entry, cfg.exit,
                   gen.solution)
        return gen

    maze = build(cfg.seed)
    print(f"Maze written to '{cfg.output_file}'")
    run_display(maze, lambda: build(None))


def main() -> int:
    """Check the arguments and run, turning any error into a clean message."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        run(sys.argv[1])
    except (ConfigError, OutputError, ValueError) as err:
        print(f"Error: {err}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as err:
        print(f"Unexpected error: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

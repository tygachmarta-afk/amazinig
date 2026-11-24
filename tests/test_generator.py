import pytest
from mazegen.generator import (
    MazeGenerator,
    has_open_3x3,
    corners_and_center_open,
    has_two_routes,
)


@pytest.mark.parametrize("seed", range(50))
def test_no_open_3x3(seed: int) -> None:
    gen = MazeGenerator(
        15, 11, (0, 0), (14, 10), perfect=False, seed=seed
    )
    gen.generate()
    assert not has_open_3x3(gen.grid)


@pytest.mark.parametrize("seed", range(50))
def test_corners_and_center_open(seed: int) -> None:
    gen = MazeGenerator(
        15, 11, (0, 0), (14, 10), perfect=False, seed=seed
    )
    gen.generate()
    assert corners_and_center_open(gen.grid)


@pytest.mark.parametrize("seed", range(50))
def test_solution_not_empty(seed: int) -> None:
    gen = MazeGenerator(15, 11, (0, 0), (14, 10), perfect=False, seed=seed)
    gen.generate()
    assert gen.solution


def test_entry_equals_exit_raises() -> None:
    with pytest.raises(ValueError):
        MazeGenerator(15, 11, (0, 0), (0, 0))


@pytest.mark.parametrize(
    "width, height, entry, exit_",
    [
        (1, 11, (0, 0), (0, 5)),     # width troppo piccola
        (15, 1, (0, 0), (5, 0)),     # height troppo piccola
        (15, 11, (99, 0), (0, 0)),   # entry fuori
        (15, 11, (0, 0), (0, 99)),   # exit fuori
        (15, 11, (3, 3), (3, 3)),    # entry == exit
    ],
)
def test_invalid_parameters(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> None:
    with pytest.raises(ValueError):
        MazeGenerator(width, height, entry, exit_)


def test_entry_inside_42_raises() -> None:
    gen = MazeGenerator(15, 11, (4, 3), (14, 10))
    with pytest.raises(ValueError):
        gen.generate()


@pytest.mark.parametrize("seed", range(50))
def test_perfect_has_single_route(seed: int) -> None:
    gen = MazeGenerator(15, 11, (0, 0), (14, 10), perfect=True, seed=seed)
    gen.generate()
    assert not has_two_routes(gen.grid, gen.entry, gen.exit)


@pytest.mark.parametrize("seed", range(50))
def test_non_perfect_has_two_routes(seed: int) -> None:
    gen = MazeGenerator(15, 11, (0, 0), (14, 10), perfect=False, seed=seed)
    gen.generate()
    assert has_two_routes(gen.grid, gen.entry, gen.exit)


@pytest.mark.parametrize("width, height", [(15, 11), (21, 15), (9, 7)])
@pytest.mark.parametrize("seed", range(30))
def test_all_rules_many_sizes(seed: int, width: int, height: int) -> None:
    gen = MazeGenerator(
        width, height,
        (0, 0),
        (width - 1, height - 1),
        perfect=False, seed=seed
    )
    gen.generate()
    assert not has_open_3x3(gen.grid)
    assert corners_and_center_open(gen.grid)
    assert gen.solution

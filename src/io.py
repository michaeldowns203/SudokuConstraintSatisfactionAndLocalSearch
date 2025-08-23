from pathlib import Path
from typing import List

QMARK = "?"

Grid = List[List[int]]


def read_puzzle(path: str | Path) -> Grid:
    """Read a 9x9 Sudoku puzzle; '?' => 0. Validates basic shape.
    Input format: 9 lines, 9 space-separated tokens per line.
    """
    p = Path(path)
    assert p.exists(), f"Puzzle path not found: {p}"
    rows: List[List[int]] = []
    for line in p.read_text().strip().splitlines():
        tokens = line.strip().split()
        if not tokens:
            continue
        row: List[int] = []
        for tok in tokens:
            if tok == QMARK:
                row.append(0)
            else:
                try:
                    v = int(tok)
                except ValueError:
                    raise ValueError(f"Invalid token '{tok}' in puzzle file {p}")
                if not (0 <= v <= 9):
                    raise ValueError(f"Out-of-range value {v} in {p}")
                row.append(v)
                rows.append(row)
                if len(rows) != 9 or any(len(r) != 9 for r in rows):
                    raise ValueError(f"Puzzle must be 9x9; got {len(rows)} rows and {[len(r) for r in rows]}")
        return rows


def write_puzzle(grid: Grid, output_filename: str | Path) -> None:
    """Write a solved grid in the exact input format (space-separated digits)."""
    out = Path(output_filename)
    lines = [" ".join(str(v) for v in row) for row in grid]
    out.write_text("\n".join(lines) + "\n")


def parse_puzzle_number(puzzle_path: str | Path) -> str:
    """Extracts the stem of the puzzle file name (e.g., 'puzzle01' from 'puzzle01.txt')."""
    stem = Path(puzzle_path).stem
    return stem


def build_output_filename(group_id: str, algorithm: str, puzzle_type: str, puzzle_path: str | Path) -> str:
    """Build output file name: [GROUP]_[ALG]_[TYPE]_[PUZZLE_NUMBER].txt"""
    puzzle_num = parse_puzzle_number(puzzle_path)
    fname = f"{group_id}_{algorithm}_{puzzle_type}_{puzzle_num}.txt"
    return fname


def validate_solution(grid: Grid) -> bool:
    """Quick validator: rows, cols, and 3x3 blocks must each be 1..9 exactly once."""
    def ok_1to9(seq: list[int]) -> bool:
        return sorted(seq) == [1,2,3,4,5,6,7,8,9]

    # rows
    for r in range(9):
        if not ok_1to9(grid[r]):
            return False
    # cols
    for c in range(9):
        if not ok_1to9([grid[r][c] for r in range(9)]):
            return False
    # blocks
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = [grid[r][c] for r in range(br, br+3) for c in range(bc, bc+3)]
            if not ok_1to9(block):
                return False
    return True
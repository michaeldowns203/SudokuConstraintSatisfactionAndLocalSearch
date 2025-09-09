from pathlib import Path
from typing import List

QMARK = "?"

Grid = List[List[int]]

def read_puzzle(path: str | Path) -> Grid:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    text = p.read_text(encoding="utf-8-sig")
    rows: list[list[int]] = []

    for line, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        tokens = raw.split(',')

        row: list[int] = []
        for tok in tokens:
            if tok == QMARK:
                row.append(0)
            else:
                row.append(int(tok))
        rows.append(row)
    return rows


def write_puzzle(grid: Grid, output_filename: str | Path) -> None:
    out = Path(output_filename)
    lines = [",".join(str(v) for v in row) for row in grid]
    out.write_text("\n".join(lines) + "\n")


def parse_puzzle_number(puzzle_path: str | Path) -> str:
    stem = Path(puzzle_path).stem
    return stem


def build_output_filename(group_id: str, algorithm: str, puzzle_type: str, puzzle_path: str | Path) -> str:
    puzzle_num = parse_puzzle_number(puzzle_path)
    fname = f"{group_id}_{algorithm}_{puzzle_type}_{puzzle_num}.txt"
    return fname


def validate_solution(grid: Grid) -> bool:
    def is_valid(seq: list[int]) -> bool:
        return sorted(seq) == [1,2,3,4,5,6,7,8,9]
    # rows
    for r in range(9):
        if not is_valid(grid[r]):
            return False
    # cols
    for c in range(9):
        if not is_valid([grid[r][c] for r in range(9)]):
            return False
    # blocks
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = [grid[r][c] for r in range(br, br+3) for c in range(bc, bc+3)]
            if not is_valid(block):
                return False
    return True
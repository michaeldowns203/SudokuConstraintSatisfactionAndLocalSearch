from pathlib import Path
from typing import List

QMARK = "?"

Grid = List[List[int]]

def read_puzzle(path: str | Path) -> Grid:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    text = p.read_text(encoding="utf-8-sig")  # strips BOM if present
    rows: list[list[int]] = []

    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        # The input uses spaces between values
        tokens = raw.split()
        if len(tokens) != 9:
            raise ValueError(f"Line {lineno}: expected 9 values, got {len(tokens)}")

        row: list[int] = []
        for tok in tokens:
            if tok == QMARK:
                row.append(0)
            else:
                try:
                    v = int(tok)
                except ValueError:
                    raise ValueError(f"Line {lineno}: invalid token {tok!r}")
                if not (0 <= v <= 9):
                    raise ValueError(f"Line {lineno}: out-of-range value {v}")
                row.append(v)
        rows.append(row)

    if len(rows) != 9:
        raise ValueError(f"Puzzle must be 9x9; got {len(rows)} rows")
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

# put this anywhere convenient (e.g., src/io.py or a debug cell)
def assert_givens_consistent(grid):
    """Raise with details if any row/col/block has duplicate givens (nonzero)."""
    def dup_positions(vals):
        seen = {}
        dups = []
        for idx, v in enumerate(vals):
            if v == 0:
                continue
            if v in seen:
                dups.append((seen[v], idx, v))
            else:
                seen[v] = idx
        return dups

    # rows
    for r in range(9):
        d = dup_positions(grid[r])
        if d:
            pairs = ", ".join(f"c{c1+1}&c{c2+1}={v}" for c1, c2, v in d)
            raise ValueError(f"Conflicting givens in ROW {r+1}: {pairs}")

    # cols
    for c in range(9):
        col = [grid[r][c] for r in range(9)]
        d = dup_positions(col)
        if d:
            pairs = ", ".join(f"r{r1+1}&r{r2+1}={v}" for r1, r2, v in d)
            raise ValueError(f"Conflicting givens in COL {c+1}: {pairs}")

    # blocks
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = []
            pos = []
            for r in range(br, br+3):
                for c in range(bc, bc+3):
                    block.append(grid[r][c]); pos.append((r, c))
            d = []
            seen = {}
            for k, v in enumerate(block):
                if v == 0:
                    continue
                if v in seen:
                    d.append((seen[v], k, v))
                else:
                    seen[v] = k
            if d:
                pretty = []
                for i1, i2, v in d:
                    r1, c1 = pos[i1]; r2, c2 = pos[i2]
                    pretty.append(f"(r{r1+1},c{c1+1}) & (r{r2+1},c{c2+1}) = {v}")
                raise ValueError(f"Conflicting givens in 3x3 block at r{br+1}..{br+3}, c{bc+1}..{bc+3}: " + ", ".join(pretty))


def assert_feasible_domains(grid):
    """Raise with exact locations if any blank has zero legal digits."""

    def candidates(r, c):
        if grid[r][c] != 0:
            return {grid[r][c]}
        used = set()
        used |= {grid[r][cc] for cc in range(9) if grid[r][cc] != 0}
        used |= {grid[rr][c] for rr in range(9) if grid[rr][c] != 0}
        br, bc = (r // 3) * 3, (c // 3) * 3
        used |= {grid[rr][cc] for rr in range(br, br + 3) for cc in range(bc, bc + 3) if grid[rr][cc] != 0}
        return {d for d in range(1, 10) if d not in used}

    bad = []
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                cands = candidates(r, c)
                if not cands:
                    bad.append((r, c))
    if bad:
        msg = ", ".join(f"(r{r + 1},c{c + 1})" for r, c in bad)
        raise ValueError(f"Unsolvable start: these blanks have NO legal digits: {msg}")

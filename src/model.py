from dataclasses import dataclass
from typing import Dict, Set, List, Tuple

Var = int # variable index 0..80
Value = int # 1..9
Domain = Set[Value]
Domains = Dict[Var, Domain]
Neighbors = Dict[Var, Set[Var]]
Grid = List[List[int]]


def rc_to_idx(r: int, c: int) -> Var:
    return r * 9 + c


def idx_to_rc(i: Var) -> Tuple[int, int]:
    return divmod(i, 9)


def block_index(r: int, c: int) -> int:
    return (r // 3) * 3 + (c // 3)


def build_neighbors() -> Neighbors:
    """Precompute peers for all 81 cells."""
    neighbors: Neighbors = {i: set() for i in range(81)}
    for r in range(9):
        for c in range(9):
            i = rc_to_idx(r, c)
            # row peers
            for cc in range(9):
                if cc != c:
                    neighbors[i].add(rc_to_idx(r, cc))
            # col peers
            for rr in range(9):
                if rr != r:
                    neighbors[i].add(rc_to_idx(rr, c))
            # block peers
            br, bc = (r // 3) * 3, (c // 3) * 3
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    j = rc_to_idx(rr, cc)
                    if j != i:
                        neighbors[i].add(j)
    return neighbors


NEIGHBORS: Neighbors = build_neighbors()


@dataclass
class SudokuCSP:
    domains: Domains # current domain per var
    fixed: Set[Var] # vars that were given in the puzzle (singleton domains)

    @classmethod
    def from_grid(cls, grid: Grid) -> "SudokuCSP":
        domains: Domains = {}
        fixed: Set[Var] = set()
        for r in range(9):
            for c in range(9):
                i = rc_to_idx(r, c)
                v = grid[r][c]
                if v == 0:
                    domains[i] = set(range(1, 10))
                else:
                    domains[i] = {v}
                    fixed.add(i)
        return cls(domains=domains, fixed=fixed)

def is_assignment_complete(self, assignment: Dict[Var, Value]) -> bool:
    return len(assignment) == 81

def is_consistent(self, var: Var, val: Value, assignment: Dict[Var, Value]) -> bool:
    """Check against assigned neighbors only."""
    for nb in NEIGHBORS[var]:
        if nb in assignment and assignment[nb] == val:
            return False
    return True

def assignment_to_grid(self, assignment: Dict[Var, Value]) -> Grid:
    grid: Grid = [[0]*9 for _ in range(9)]
    for i, v in assignment.items():
        r, c = idx_to_rc(i)
        grid[r][c] = v
    return grid
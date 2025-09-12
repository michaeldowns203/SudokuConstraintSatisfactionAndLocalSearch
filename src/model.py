from dataclasses import dataclass
from typing import Dict, Set, List, Tuple

Index = int # 0..80
Value = int # 1..9
Domain = Set[Value]
Domains = Dict[Index, Domain]
Neighbors = Dict[Index, Set[Index]]
Grid = List[List[int]]


def rc_to_idx(r: int, c: int) -> Index:
    return r * 9 + c


def idx_to_rc(i: Index) -> Tuple[int, int]:
    return divmod(i, 9)


def block_index(r: int, c: int) -> int:
    return (r // 3) * 3 + (c // 3)


def build_neighbors() -> Neighbors:
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
class DomainManager:
    domains: Domains # current domains
    fixed_values: Set[Index] # given values (singleton domains)

    @classmethod
    def from_grid(cls, grid: Grid) -> "DomainManager":
        domains: Domains = {}
        fixed: Set[Index] = set()
        for r in range(9):
            for c in range(9):
                i = rc_to_idx(r, c)
                v = grid[r][c]
                if v == 0:
                    domains[i] = set(range(1, 10))
                else:
                    domains[i] = {v}
                    fixed.add(i)
        return cls(domains=domains, fixed_values=fixed)

def is_assignment_complete(assignment: Dict[Index, Value]) -> bool:
    return len(assignment) == 81

def is_consistent(idx: Index, val: Value, assignment: Dict[Index, Value], metrics) -> bool:
    # Check against assigned neighbors only
    for nb in NEIGHBORS[idx]:
        if nb in assignment:
            metrics.constraint_checks += 1
            if assignment[nb] == val:
                return False
    return True

def assignment_to_grid(assignment: Dict[Index, Value]) -> Grid:
    grid: Grid = [[0]*9 for _ in range(9)]
    for i, v in assignment.items():
        r, c = idx_to_rc(i)
        grid[r][c] = v
    return grid
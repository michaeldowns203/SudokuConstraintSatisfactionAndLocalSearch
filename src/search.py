from collections import deque
from typing import Dict, Optional, List, Tuple
from copy import deepcopy
from .model import DomainManager, Index, Value, Domains, NEIGHBORS, is_consistent
from .metrics import Metrics

# -------------------- Heuristic hooks --------------------

def select_unassigned_idx_default(assignment: Dict[Index, Value]) -> Index:
    for i in range(81):
        if i not in assignment:
            return i
    raise RuntimeError("No unassigned var found")


def select_unassigned_idx_mrv_degree(domain_manager: DomainManager, assignment: Dict[Index, Value]) -> Index:
    """TODO or not?: choose var with MRV, break ties by degree (most unassigned neighbors)."""
    return select_unassigned_idx_default(assignment)


def order_domain_values_default(domain_manager: DomainManager, var: Index) -> List[Value]:
    return sorted(domain_manager.domains[var])


def order_domain_values_lcv(domain_manager: DomainManager, var: Index, assignment: Dict[Index, Value]) -> List[Value]:
    """TODO or not?: order by least-constraining value (min impact on neighbors)."""
    return order_domain_values_default(domain_manager, var)

# -------------------- Inference hooks --------------------

class Trail:
    def __init__(self):
        self._stack: List[Tuple[Index, Value]] = []

    def prune(self, domains: Domains, idx: Index, val: Value) -> None:
        if val in domains[idx]:
            domains[idx].remove(val)
            self._stack.append((idx, val))

    def undo(self, domains: Domains) -> None:
        while self._stack:
            var, val = self._stack.pop()
            domains[var].add(val)


def forward_check(domains: Domains, idx: Index, val: Value, metrics: Metrics) -> Optional[Trail]:
    trail = Trail()

    for nb in NEIGHBORS:
        if nb == idx:
            continue
        if val in domains[nb]:
            trail.prune(domains, nb, val)
            metrics.inferences += 1
            if not domains[nb]:
                trail.undo(domains)

    return trail


def ac3(domains: Domains, metrics: Metrics) -> bool:
    queue = deque((i, j) for i in NEIGHBORS for j in NEIGHBORS[i])

    def revise(i: Index, j: Index) -> bool:
        to_remove: List[Value] = []
        for a in domains[i]:
            # For Sudoku '!=', a has support in j if there exists b != a in D(j)
            if all(b == a for b in domains[j]):
                metrics.inferences += 1
                to_remove.append(a)
        if not to_remove:
            return False
        for a in to_remove:
            domains[i].remove(a)
        return True

    while queue:
        i, j = queue.popleft()
        if revise(i, j):
            if not domains[i]:
                return False  # domain wipeout
            for k in NEIGHBORS[i]:
                if k != j:
                    queue.append((k, i))
    return True

# -------------------- Core backtracking --------------------

def backtracking(
    domain_manager: DomainManager,
    mode: str,  # 'bt' | 'fc' | 'ac3'
    metrics: Metrics,
    var_heuristic: str = 'default',
    val_heuristic: str = 'default',
) -> Optional[Dict[Index, Value]]:

    domains: Domains = deepcopy(domain_manager.domains)
    assignment: Dict[Index, Value] = {
        i: next(iter(domains[i])) for i in range(81) if len(domains[i]) == 1
    }

    if var_heuristic == 'mrv-degree':
        select_idx = lambda a: select_unassigned_idx_mrv_degree(domain_manager, a)
    else:
        select_idx = select_unassigned_idx_default

    if val_heuristic == 'lcv':
        order_vals = lambda v, a: order_domain_values_lcv(domain_manager, v, a)
    else:
        order_vals = lambda v, a: order_domain_values_default(domain_manager, v)

    def backtrack() -> Optional[Dict[Index, Value]]:
        if len(assignment) == 81:
            return assignment

        idx = select_idx(assignment)

        for val in order_vals(idx, assignment):
            if val not in domains[idx]:
                continue
            if not is_consistent(idx, val, assignment):
                continue

            assignment[idx] = val
            metrics.assignments += 1

            ok = True
            trail = None
            saved_domain = None

            if mode == 'fc':
                trail = forward_check(domains, idx, val, metrics)
                if trail is None:
                    ok = False
            elif mode == 'ac3':
                saved_domain = domains[idx].copy()
                domains[idx] = {val}
                ok = ac3(domains, metrics)

            if ok:
                result = backtrack()
                if result is not None:
                    return result

            if mode == 'fc' and trail is not None:
                trail.undo(domains)
            elif mode == 'ac3' and saved_domain is not None:
                domains[idx] = saved_domain

            del assignment[idx]
            metrics.backtracks += 1

        return None

    return backtrack()
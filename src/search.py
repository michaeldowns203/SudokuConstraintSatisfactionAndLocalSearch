from collections import deque
from typing import Dict, Optional, List, Tuple
from copy import deepcopy
from .model import DomainManager, Index, Value, Domains, NEIGHBORS, is_consistent
from .metrics import Metrics


def select_unassigned_idx(assignment: Dict[Index, Value]) -> Index:
    for i in range(81):
        if i not in assignment:
            return i
    raise RuntimeError("No unassigned var found")

def order_domain_values(domains: Domains, var: Index) -> List[Value]:
    return sorted(domains[var])

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

    for nb in NEIGHBORS[idx]:
        d = domains[nb]
        # If neighbor already assigned
        if len(d) == 1:
            # Constraint violated
            metrics.constraint_checks += 1
            if val in d:
                trail.undo(domains)
                return None
            # Nothing to prune
            continue
        # Unassigned neighbor
        if val in d:
            # Remove conflicting value
            trail.prune(domains, nb, val)
            metrics.inferences += 1
            if not domains[nb]: # domain wipeout
                trail.undo(domains)
                return None

    return trail


def ac3(domains: Domains, metrics: Metrics) -> Optional[Trail]:
    trail = Trail()
    queue = deque((i, j) for i in NEIGHBORS for j in NEIGHBORS[i])

    def revise(i, j) -> bool:
        removed = False
        to_remove = []
        # remove a in D(i) if j’s domain is {a}
        for a in list(domains[i]):
            supported = any((a != b) for b in domains[j])
            metrics.constraint_checks += len(domains[j])
            if not supported:
                to_remove.append(a)
        for a in to_remove:
            trail.prune(domains, i, a)
            metrics.inferences += 1
            removed = True
        return removed

    while queue:
        i, j = queue.popleft()
        if revise(i, j):
            if not domains[i]: # domain wipeout
                trail.undo(domains)
                return None
            for nb in NEIGHBORS[i]:
                if nb != j:
                    queue.append((nb, i))
    return trail



def backtracking(
    domain_manager: DomainManager,
    mode: str,  # 'bt' | 'fc' | 'ac3'
    metrics: Metrics
) -> Optional[Dict[Index, Value]]:

    domains: Domains = deepcopy(domain_manager.domains)
    assignment: Dict[Index, Value] = {
        i: next(iter(domains[i])) for i in range(81) if len(domains[i]) == 1
    }

    select_idx = select_unassigned_idx

    order_vals = lambda v, a: order_domain_values(domains, v)

    def backtrack() -> Optional[Dict[Index, Value]]:
        if len(assignment) == 81:
            return assignment

        idx = select_idx(assignment)

        for val in order_vals(idx, assignment):
            if val not in domains[idx]:
                continue
            if not is_consistent(idx, val, assignment, metrics):
                continue

            assignment[idx] = val
            metrics.assignments += 1

            ok = True
            trail = None
            saved_domain = None

            if mode == 'fc':
                saved_domain = domains[idx].copy()
                domains[idx] = {val}
                trail = forward_check(domains, idx, val, metrics)
                if trail is None:
                    ok = False

            elif mode == 'ac3':
                saved_domain = domains[idx].copy()
                domains[idx] = {val}
                trail = ac3(domains, metrics)
                if trail is None:
                    ok = False

            if ok:
                result = backtrack()
                if result is not None:
                    return result

            if trail is not None:
                trail.undo(domains)

            if saved_domain is not None:
                domains[idx] = saved_domain

            del assignment[idx]
            metrics.backtracks += 1

        return None

    return backtrack()
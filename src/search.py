from typing import Dict, Optional, List, Tuple, Iterable
from copy import deepcopy
from .model import SudokuCSP, Var, Value, Domains, NEIGHBORS
from .metrics import Metrics

# -------------------- Heuristic hooks (fill these in later) --------------------

def select_unassigned_var_default(assignment: Dict[Var, Value]) -> Var:
    # Left-to-right
    for i in range(81):
        if i not in assignment:
            return i
    raise RuntimeError("No unassigned var found")


def select_unassigned_var_mrv_degree(csp: SudokuCSP, assignment: Dict[Var, Value]) -> Var:
    """TODO: choose var with MRV, break ties by degree (most unassigned neighbors)."""
    # Placeholder: default behavior
    return select_unassigned_var_default(assignment)


def order_domain_values_default(csp: SudokuCSP, var: Var, assignment: Dict[Var, Value]) -> List[Value]:
    return sorted(csp.domains[var])


def order_domain_values_lcv(csp: SudokuCSP, var: Var, assignment: Dict[Var, Value]) -> List[Value]:
    """TODO: order by least-constraining value (min impact on neighbors)."""
    return order_domain_values_default(csp, var, assignment)

# -------------------- Inference hooks (fill these in later) --------------------

class Trail:
    """Records domain prunings so they can be undone on backtrack."""
    def __init__(self):
        self._stack: List[Tuple[Var, Value]] = []

def prune(self, domains: Domains, var: Var, val: Value) -> None:
    if val in domains[var]:
        domains[var].remove(val)
        self._stack.append((var, val))

def undo(self, domains: Domains) -> None:
    while self._stack:
        var, val = self._stack.pop()
        domains[var].add(val)


def forward_check(csp: SudokuCSP, domains: Domains, var: Var, val: Value, metrics: Metrics) -> Optional[Trail]:
    """Prune 'val' from neighbors; if any neighbor domain becomes empty, return None.
    Return a Trail of prunings to undo later.
    """
    # TODO: implement FC; currently a no-op that succeeds
    return Trail()


def ac3(csp: SudokuCSP, domains: Domains, metrics: Metrics) -> bool:
    """AC-3 arc consistency. Return True if consistent (no empty domain)."""
    # TODO: implement AC-3; currently a no-op that returns True
    return True

# -------------------- Core backtracking --------------------

def backtracking_search(
    csp: SudokuCSP,
    mode: str, # 'bt' | 'fc' | 'ac3'
    metrics: Metrics,
    var_heuristic: str = 'default', # 'default' | 'mrv-degree'
    val_heuristic: str = 'default', # 'default' | 'lcv'
    ) -> Optional[Dict[Var, Value]]:
    """Backtracking with optional inference and heuristics.
    Returns an assignment dict if solved else None.
    """
    domains: Domains = deepcopy(csp.domains)
    assignment: Dict[Var, Value] = {i: next(iter(domains[i])) for i in range(81) if len(domains[i]) == 1}

    if var_heuristic == 'mrv-degree':
        select_var = lambda a: select_unassigned_var_mrv_degree(csp, a)
    else:
        select_var = select_unassigned_var_default

    if val_heuristic == 'lcv':
        order_vals = lambda v, a: order_domain_values_lcv(csp, v, a)
    else:
        order_vals = lambda v, a: order_domain_values_default(csp, v, a)

    def backtrack() -> Optional[Dict[Var, Value]]:
        if len(assignment) == 81:
            return assignment

        var = select_var(assignment)
        for val in order_vals(var, assignment):
            if val not in domains[var]:
                continue
            if not csp.is_consistent(var, val, assignment):
                continue
            # choose
            assignment[var] = val
            metrics.assignments += 1
            # inference
            trail = None
            if mode == 'fc':
                trail = forward_check(csp, domains, var, val, metrics)
                if trail is None:
                    # failed inference
                    del assignment[var]
                    metrics.backtracks += 1
                    continue
                elif mode == 'ac3':
                    # Assign var=val in domains for AC-3
                    saved = domains[var].copy()
                    domains[var] = {val}
                if not ac3(csp, domains, metrics):
                    # restore and backtrack
                    domains[var] = saved
                    del assignment[var]
                    metrics.backtracks += 1
                    continue
                # recurse
                result = backtrack()
                if result is not None:
                    return result
                # undo
                if mode == 'fc' and trail is not None:
                    trail.undo(domains)
                if mode == 'ac3':
                    domains[var] = saved  # type: ignore
                del assignment[var]
                metrics.backtracks += 1
            return None
        return backtrack()
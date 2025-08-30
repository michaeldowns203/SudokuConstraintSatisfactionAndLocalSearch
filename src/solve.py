from typing import Tuple, Optional
from .io import validate_solution
from .model import SudokuCSP
from .metrics import Metrics
from .search import backtracking_search
from .local import solve_sa, solve_ga, SAConfig, GAConfig

Grid = list[list[int]]


def solve(grid: Grid, algorithm: str, seed: int = 0) -> Tuple[Optional[Grid], Metrics]:
    """Unified entry point. Returns (grid_or_None, metrics)."""
    metrics = Metrics()
    csp = SudokuCSP.from_grid(grid)

    if algorithm == 'bt':
        assignment = backtracking_search(csp, mode='bt', metrics=metrics, var_heuristic='default', val_heuristic='default')
        if assignment is None:
            return None, metrics
        solved = csp.assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'fc':
        assignment = backtracking_search(csp, mode='fc', metrics=metrics, var_heuristic='mrv-degree', val_heuristic='lcv')
        if assignment is None:
            return None, metrics
        solved = csp.assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'ac3':
        assignment = backtracking_search(csp, mode='ac3', metrics=metrics, var_heuristic='mrv-degree', val_heuristic='lcv')
        if assignment is None:
            return None, metrics
        solved = csp.assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'sa':
        cfg = SAConfig(seed=seed)
        solved = solve_sa(grid, cfg, metrics)
        return (solved if (solved and validate_solution(solved)) else None), metrics

    if algorithm == 'ga':
        cfg = GAConfig(seed=seed)
        solved = solve_ga(grid, cfg, metrics)
        return (solved if (solved and validate_solution(solved)) else None), metrics
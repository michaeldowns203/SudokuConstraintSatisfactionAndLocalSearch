from typing import Optional, Tuple
from .io import validate_solution
from .model import DomainManager, assignment_to_grid
from .metrics import Metrics
from .search import backtracking
from .local import solve_sa, solve_ga, SAConfig, GAConfig

Grid = list[list[int]]


def solve(grid: Grid, algorithm: str, seed: int = 0) -> Tuple[Optional[Grid], Metrics]:
    metrics = Metrics()
    domain_manager = DomainManager.from_grid(grid)

    if algorithm == 'bt':
        assignment = backtracking(domain_manager, mode='bt', metrics=metrics)
        if assignment is None:
            return None, metrics
        solved = assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'fc':
        assignment = backtracking(domain_manager, mode='fc', metrics=metrics)
        if assignment is None:
            return None, metrics
        solved = assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'ac3':
        assignment = backtracking(domain_manager, mode='ac3', metrics=metrics)
        if assignment is None:
            return None, metrics
        if assignment is None:
            return None, metrics
        solved = assignment_to_grid(assignment)
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'sa':
        cfg = SAConfig(domain_manager, seed=seed)
        solved = solve_sa(grid, cfg, metrics)
        if solved is None:
            return None, metrics
        return (solved if validate_solution(solved) else None), metrics

    if algorithm == 'ga':
        cfg = GAConfig(domain_manager, seed=seed)
        solved = solve_ga(grid, cfg, metrics)
        if solved is None:
            return None, metrics
        return (solved if validate_solution(solved) else None), metrics

    return None, metrics
from dataclasses import dataclass
from typing import List, Optional
import random
from .metrics import Metrics

Grid = List[List[int]]

# -------------- Simulated Annealing --------------

@dataclass
class SAConfig:
    seed: int = 0
    max_steps: int = 100000
    restarts: int = 3
    T0: float = 1.0
    cooling: float = 0.999 # geometric cooling


def solve_sa(initial_grid: Grid, cfg: SAConfig, metrics: Metrics) -> Optional[Grid]:
    """Min-conflicts SA skeleton. Fill blocks; swap within blocks; accept by SA rule.
    TODO: implement. Return solved grid or None."""
    random.seed(cfg.seed)
    # TODO: implement SA setup (fixed mask, fill blocks), conflict counters, swap loop, restarts.
    metrics.decisions += 0
    return None

# -------------- Genetic Algorithm --------------

@dataclass
class GAConfig:
    seed: int = 0
    pop_size: int = 200
    generations: int = 2000
    tournament_k: int = 3
    mutation_rate: float = 0.1
    elitism: int = 2


def solve_ga(initial_grid: Grid, cfg: GAConfig, metrics: Metrics) -> Optional[Grid]:
    """GA skeleton using block-preserving representation and penalty fitness.
    TODO: implement. Return solved grid or None."""
    random.seed(cfg.seed)
    # TODO: implement GA (init, fitness, selection, crossover, mutation, elitism)
    metrics.generations = 0
    return None
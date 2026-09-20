# Sudoku: Constraint Satisfaction and Local Search

A Sudoku solver comparing **five search strategies** through a common solver interface: plain backtracking, forward checking, arc consistency, simulated annealing, and a genetic algorithm. The experiments examine where search effort is spent, using assignments, backtracks, inferences, and constraint checks rather than relying on runtime alone.

[Read the full paper](finalPaper.pdf) · [Explore the notebook](Sudoku.ipynb) · [Source code](src/)

## Algorithms

| Identifier | Method | Main idea |
| --- | --- | --- |
| `bt` | Backtracking | Assign values and backtrack when a constraint fails. |
| `fc` | Forward checking | Remove newly invalid values from neighboring domains after an assignment. |
| `ac3` | Backtracking with arc consistency | Propagate constraints to remove unsupported domain values. |
| `sa` | Simulated annealing | Search candidate boards with temperature-controlled acceptance of worse moves. |
| `ga` | Genetic algorithm | Evolve candidate boards through selection, crossover, and mutation. |

The shared `solve(grid, algorithm, seed=0)` function returns a solution or `None`, together with collected metrics. Returned solutions are checked for validity.

## Explore and use the solver

Start with [`Sudoku.ipynb`](Sudoku.ipynb) to inspect the experiment and puzzle-generation workflow. Some experiment cells are commented out in the repository version; review and enable only the cells for the experiment you intend to run.

The programmatic entry point is [`src/solve.py`](src/solve.py):

```python
from src.io import read_puzzle
from src.solve import solve

grid = read_puzzle("puzzles/easy/Easy-P1.txt")
solution, metrics = solve(grid, algorithm="ac3", seed=0)
print(solution)
print(metrics)
```

Run this example from the repository root so the `src` package and puzzle path resolve correctly. The input reader accepts comma-separated rows and converts `?` cells to zero internally. The notebook's import cells identify the dependencies needed for its plotting and analysis workflow.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`src/model.py`](src/model.py) | Domains and puzzle representation. |
| [`src/search.py`](src/search.py) | Backtracking, forward checking, and arc consistency. |
| [`src/local.py`](src/local.py) | Simulated annealing and genetic search. |
| [`src/solve.py`](src/solve.py) | Unified solver interface. |
| [`src/io.py`](src/io.py) | Input and solution validation. |
| [`src/metrics.py`](src/metrics.py), [`metrics/`](metrics/) | Instrumentation and saved measurements. |

## Limitations

Decision counts do not measure the same kind of work for every algorithm, and the local-search runs depend on random initialization, tuning, and stopping limits. The results apply to the supplied puzzle collection and configurations.

## Contributors

As documented in the paper:

- **Michael Downs:** backtracking, forward checking, and arc consistency; descriptions of those algorithms.
- **Sadman Sakib:** simulated annealing and the genetic algorithm; descriptions of those algorithms.
- **Chance Larson:** metrics definition, data collection, and graph creation; abstract, problem statement/hypothesis, results, graphs, discussion, and summary.

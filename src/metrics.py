from dataclasses import dataclass, field

@dataclass
class Metrics:
    assignments: int = 0
    backtracks: int = 0
    inferences: int = 0 # prunings/arc revisions
    constraint_checks: int = 0

    # Local-search oriented
    decisions: int = 0
    restarts: int = 0
    generations: int = 0

    trace: list = field(default_factory=list)

    def reset(self) -> None:
        self.assignments = self.backtracks = self.inferences = 0
        self.decisions = self.restarts = self.generations = 0
        self.trace.clear()

    def __str__(self) -> str:
        return (
        f"constrain checks={self.constraint_checks} assignments={self.assignments}, backtracks={self.backtracks}, "
        f"inferences={self.inferences}, decisions={self.decisions}, "
        f"restarts={self.restarts}, generations={self.generations}"
        )
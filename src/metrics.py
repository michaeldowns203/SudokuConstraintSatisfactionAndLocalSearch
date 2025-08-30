from dataclasses import dataclass, field

@dataclass
class Metrics:
    assignments: int = 0 # count of value placements attempted
    backtracks: int = 0 # count of times we backed up
    inferences: int = 0 # prunings/arc revisions

    # Local-search oriented
    decisions: int = 0 # e.g., SA swaps or GA ops
    restarts: int = 0
    generations: int = 0

    trace: list = field(default_factory=list) # append key events

    def reset(self) -> None:
        self.assignments = self.backtracks = self.inferences = 0
        self.decisions = self.restarts = self.generations = 0
        self.trace.clear()

    def __str__(self) -> str:
        return (
        f"assignments={self.assignments}, backtracks={self.backtracks}, "
        f"inferences={self.inferences}, decisions={self.decisions}, "
        f"restarts={self.restarts}, generations={self.generations}"
        )
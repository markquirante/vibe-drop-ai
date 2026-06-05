from dataclasses import dataclass
from typing import Protocol

from vibedrop_ai.domain import ChordMidiPlan


@dataclass(frozen=True)
class ChordEventPlannerRequest:
    prompt: str
    key: str | None = None
    scale: str | None = None
    tempo_bpm: int | None = None
    bars: int | None = None
    style: str | None = None


class ChordEventPlanner(Protocol):
    def plan_from_prompt(self, request: ChordEventPlannerRequest) -> ChordMidiPlan:
        """Return an AI-authored chord MIDI event plan for the prompt."""


class PlannerUnavailableError(RuntimeError):
    pass


class UnconfiguredChordEventPlanner:
    def plan_from_prompt(self, request: ChordEventPlannerRequest) -> ChordMidiPlan:
        raise PlannerUnavailableError(
            "No chord event planner is configured. Use a local JSON chord event plan "
            "or provide an AI-backed ChordEventPlanner implementation."
        )

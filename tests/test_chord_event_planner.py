import pytest

from vibedrop_ai.planning.chord_event_planner import (
    ChordEventPlannerRequest,
    PlannerUnavailableError,
    UnconfiguredChordEventPlanner,
)


def test_chord_event_planner_request_captures_prompt_constraints():
    request = ChordEventPlannerRequest(
        prompt="Make a dusty lo-fi C minor chord loop.",
        key="C",
        scale="minor",
        tempo_bpm=85,
        bars=4,
        style="lofi",
    )

    assert request.prompt == "Make a dusty lo-fi C minor chord loop."
    assert request.key == "C"
    assert request.scale == "minor"
    assert request.tempo_bpm == 85
    assert request.bars == 4
    assert request.style == "lofi"


def test_unconfigured_chord_event_planner_fails_explicitly():
    planner = UnconfiguredChordEventPlanner()
    request = ChordEventPlannerRequest(prompt="Make a C minor chord loop.")

    with pytest.raises(PlannerUnavailableError, match="No chord event planner is configured"):
        planner.plan_from_prompt(request)

import pytest

from vibedrop_ai.domain import CompositionPlan, TrackSpec
from vibedrop_ai.generation_service import generate_from_plan


def make_valid_plan() -> CompositionPlan:
    return CompositionPlan(
        key="C",
        scale="minor",
        tempo_bpm=85,
        bars=4,
        style="lofi",
        seed=123,
        tracks=[
            TrackSpec(role="chords", channel=0),
            TrackSpec(role="melody", channel=1),
        ],
    )


def test_generate_from_plan_creates_midi_file(tmp_path):
    plan = make_valid_plan()
    output_path = tmp_path / "idea.mid"

    artifact = generate_from_plan(plan, output_path)

    assert artifact.path == output_path
    assert artifact.plan == plan
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_from_plan_rejects_invalid_plan(tmp_path):
    valid_plan = make_valid_plan()
    invalid_plan = CompositionPlan(
        key="H",
        scale=valid_plan.scale,
        tempo_bpm=valid_plan.tempo_bpm,
        bars=valid_plan.bars,
        style=valid_plan.style,
        seed=valid_plan.seed,
        tracks=valid_plan.tracks,
    )

    with pytest.raises(ValueError, match="Invalid composition plan"):
        generate_from_plan(invalid_plan, tmp_path / "bad.mid")

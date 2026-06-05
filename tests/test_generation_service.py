import pytest

from vibedrop_ai.domain import ChordMidiPlan, ChordNoteEvent, ChordTrackPlan
from vibedrop_ai.generation_service import generate_from_plan, generate_from_prompt
from vibedrop_ai.planning.chord_event_planner import ChordEventPlannerRequest


def make_valid_plan() -> ChordMidiPlan:
    return ChordMidiPlan(
        key="C",
        scale="minor",
        tempo_bpm=85,
        bars=1,
        style="lofi",
        tracks=[
            ChordTrackPlan(
                name="Lo-fi Rhodes Chords",
                channel=0,
                events=[
                    ChordNoteEvent(
                        pitch=60,
                        start_beat=0,
                        duration_beats=4,
                        velocity=76,
                        channel=0,
                        chord_label="Cm7",
                    ),
                    ChordNoteEvent(
                        pitch=63,
                        start_beat=0,
                        duration_beats=4,
                        velocity=72,
                        channel=0,
                        chord_label="Cm7",
                    ),
                ],
            )
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
    invalid_plan = ChordMidiPlan(
        key="H",
        scale=valid_plan.scale,
        tempo_bpm=valid_plan.tempo_bpm,
        bars=valid_plan.bars,
        style=valid_plan.style,
        tracks=valid_plan.tracks,
    )

    with pytest.raises(ValueError, match="Invalid chord MIDI plan"):
        generate_from_plan(invalid_plan, tmp_path / "bad.mid")


def test_generate_from_prompt_uses_planner_and_saves_plan_json(tmp_path):
    plan = make_valid_plan()
    output_path = tmp_path / "idea.mid"
    plan_output_path = tmp_path / "idea.plan.json"

    class FakePlanner:
        def plan_from_prompt(self, request):
            assert request.prompt == "Make a dusty C minor chord loop."
            return plan

    artifact = generate_from_prompt(
        request=ChordEventPlannerRequest(prompt="Make a dusty C minor chord loop."),
        output_path=output_path,
        planner=FakePlanner(),
        plan_output_path=plan_output_path,
    )

    assert artifact.path == output_path
    assert artifact.plan == plan
    assert output_path.exists()
    assert plan_output_path.exists()
    assert '"pitch": 60' in plan_output_path.read_text()

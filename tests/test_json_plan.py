import json

from vibedrop_ai.domain import (
    ChordMidiPlan,
    ChordNoteEvent,
    ChordTrackPlan,
    CompositionPlan,
    TrackSpec,
)
from vibedrop_ai.planning.json_plan import load_chord_midi_plan, load_composition_plan


def test_load_comp_plan_loads_valid_json_file(tmp_path):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "key": "C",
                "scale": "minor",
                "tempo_bpm": 85,
                "bars": 4,
                "style": "lofi",
                "seed": 123,
                "tracks": [
                    {"role": "chords", "channel": 0},
                    {"role": "melody", "channel": 1},
                ],
            }
        )
    )

    plan = load_composition_plan(plan_path)

    assert plan == CompositionPlan(
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


def test_load_comp_plan_allows_missing_seed(tmp_path):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "key": "C",
                "scale": "minor",
                "tempo_bpm": 85,
                "bars": 4,
                "style": "lofi",
                "tracks": [
                    {"role": "chords", "channel": 0},
                ],
            }
        )
    )

    plan = load_composition_plan(plan_path)

    assert plan.seed is None
    assert plan.tracks == [TrackSpec(role="chords", channel=0)]


def test_load_chord_midi_plan_loads_event_json_file(tmp_path):
    plan_path = tmp_path / "chord_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "key": "C",
                "scale": "minor",
                "tempo_bpm": 85,
                "bars": 1,
                "style": "lofi",
                "time_signature": {
                    "numerator": 4,
                    "denominator": 4,
                },
                "tracks": [
                    {
                        "name": "Lo-fi Rhodes Chords",
                        "channel": 0,
                        "events": [
                            {
                                "pitch": 60,
                                "start_beat": 0,
                                "duration_beats": 4,
                                "velocity": 76,
                                "chord_label": "Cm7",
                            }
                        ],
                    }
                ],
            }
        )
    )

    plan = load_chord_midi_plan(plan_path)

    assert plan == ChordMidiPlan(
        key="C",
        scale="minor",
        tempo_bpm=85,
        bars=1,
        style="lofi",
        time_signature_numerator=4,
        time_signature_denominator=4,
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
                    )
                ],
            )
        ],
    )


def test_load_chord_midi_plan_defaults_missing_event_values(tmp_path):
    plan_path = tmp_path / "chord_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "key": "C",
                "scale": "minor",
                "tempo_bpm": 85,
                "bars": 1,
                "style": "lofi",
                "tracks": [
                    {
                        "name": "Lo-fi Rhodes Chords",
                        "channel": 2,
                        "events": [
                            {
                                "pitch": 60,
                                "start_beat": 0,
                                "duration_beats": 4,
                            }
                        ],
                    }
                ],
            }
        )
    )

    plan = load_chord_midi_plan(plan_path)
    event = plan.tracks[0].events[0]

    assert plan.time_signature_numerator == 4
    assert plan.time_signature_denominator == 4
    assert event.velocity == 80
    assert event.channel == 2
    assert event.chord_label is None

import json

from vibedrop_ai.domain import CompositionPlan, TrackSpec
from vibedrop_ai.planning.json_plan import load_composition_plan


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

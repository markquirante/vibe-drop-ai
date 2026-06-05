import json

import pytest

from vibedrop_ai.planning.chord_event_planner import (
    ChordEventPlannerRequest,
    PlannerUnavailableError,
)
from vibedrop_ai.planning.gemini_chord_event_planner import (
    GeminiChordEventPlanner,
    chord_midi_plan_from_dict,
)


def test_chord_midi_plan_from_dict_maps_gemini_json_to_domain_model():
    plan = chord_midi_plan_from_dict(
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
                            "channel": 0,
                            "chord_label": "Cm7",
                        }
                    ],
                }
            ],
        }
    )

    assert plan.key == "C"
    assert plan.scale == "minor"
    assert plan.time_signature_numerator == 4
    assert plan.tracks[0].events[0].pitch == 60
    assert plan.tracks[0].events[0].chord_label == "Cm7"


def test_gemini_chord_event_planner_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    planner = GeminiChordEventPlanner(api_key=None)

    with pytest.raises(PlannerUnavailableError, match="GEMINI_API_KEY is not set"):
        planner.plan_from_prompt(ChordEventPlannerRequest(prompt="Make a chord loop."))


def test_gemini_chord_event_planner_parses_response_without_live_api():
    class FakeGeminiPlanner(GeminiChordEventPlanner):
        def _post_json(self, payload):
            assert payload["generationConfig"]["responseMimeType"] == "application/json"
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
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
                                                            "channel": 0,
                                                            "chord_label": "Cm7",
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    )
                                }
                            ]
                        }
                    }
                ]
            }

    planner = FakeGeminiPlanner(api_key="test-key")

    plan = planner.plan_from_prompt(
        ChordEventPlannerRequest(
            prompt="Make a dusty C minor chord loop.",
            key="C",
            scale="minor",
            tempo_bpm=85,
            bars=1,
            style="lofi",
        )
    )

    assert plan.key == "C"
    assert plan.tracks[0].events[0].pitch == 60

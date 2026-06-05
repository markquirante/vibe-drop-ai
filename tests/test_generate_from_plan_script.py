import json

from vibedrop_ai.scripts.generate_from_plan import main


def test_generate_from_plan_script_creates_midi_file(tmp_path):
    plan_path = tmp_path / "plan.json"
    output_path = tmp_path / "idea.mid"
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
                        "channel": 0,
                        "events": [
                            {
                                "pitch": 60,
                                "start_beat": 0,
                                "duration_beats": 4,
                                "velocity": 76,
                                "chord_label": "Cm7",
                            },
                            {
                                "pitch": 63,
                                "start_beat": 0,
                                "duration_beats": 4,
                                "velocity": 72,
                                "chord_label": "Cm7",
                            },
                        ],
                    }
                ],
            }
        )
    )

    exit_code = main([str(plan_path), str(output_path)])

    assert exit_code == 0
    assert output_path.exists()
    assert output_path.stat().st_size > 0

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

    exit_code = main([str(plan_path), str(output_path)])

    assert exit_code == 0
    assert output_path.exists()
    assert output_path.stat().st_size > 0

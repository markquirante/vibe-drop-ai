from vibedrop_ai.domain import CompositionPlan, TrackSpec
from vibedrop_ai.validation.music_theory import validate_composition_plan


def make_valid_plan(**overrides) -> CompositionPlan:
    values = {
        "key": "C",
        "scale": "minor",
        "tempo_bpm": 85,
        "bars": 4,
        "style": "lofi",
        "seed": 123,
        "tracks": [
            TrackSpec(role="chords", channel=0),
        ],
    }
    values.update(overrides)
    return CompositionPlan(**values)


def assert_has_error_field(plan: CompositionPlan, field: str) -> None:
    result = validate_composition_plan(plan)

    assert not result.is_valid
    assert any(error.field == field for error in result.errors)


def test_valid_composition_plan_passes():
    result = validate_composition_plan(make_valid_plan())

    assert result.is_valid
    assert result.errors == []


def test_invalid_key_fails():
    assert_has_error_field(make_valid_plan(key="H"), "key")


def test_invalid_scale_fails():
    assert_has_error_field(make_valid_plan(scale="dorian"), "scale")


def test_invalid_tempo_fails():
    assert_has_error_field(make_valid_plan(tempo_bpm=300), "tempo_bpm")


def test_invalid_bars_fails():
    assert_has_error_field(make_valid_plan(bars=0), "bars")


def test_unsupported_style_fails():
    assert_has_error_field(make_valid_plan(style="trap"), "style")


def test_empty_tracks_fails():
    assert_has_error_field(make_valid_plan(tracks=[]), "tracks")


def test_duplicate_track_role_fails():
    plan = make_valid_plan(
        tracks=[
            TrackSpec(role="chords", channel=0),
            TrackSpec(role="chords", channel=1),
        ]
    )

    assert_has_error_field(plan, "tracks[1].role")


def test_duplicate_midi_channel_fails():
    plan = make_valid_plan(
        tracks=[
            TrackSpec(role="chords", channel=0),
            TrackSpec(role="pad", channel=0),
        ]
    )

    assert_has_error_field(plan, "tracks[1].channel")


def test_invalid_midi_channel_fails():
    plan = make_valid_plan(
        tracks=[
            TrackSpec(role="chords", channel=16),
        ]
    )

    assert_has_error_field(plan, "tracks[0].channel")


def test_negative_seed_fails():
    assert_has_error_field(make_valid_plan(seed=-1), "seed")


def test_melody_track_role_fails():
    plan = make_valid_plan(
        tracks=[
            TrackSpec(role="melody", channel=1),
        ]
    )

    assert_has_error_field(plan, "tracks[0].role")

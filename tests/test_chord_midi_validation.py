from dataclasses import replace

from vibedrop_ai.domain import ChordMidiPlan, ChordNoteEvent, ChordTrackPlan
from vibedrop_ai.validation.chord_midi import validate_chord_midi_plan


def make_valid_plan(event: ChordNoteEvent | None = None) -> ChordMidiPlan:
    if event is None:
        event = ChordNoteEvent(
            pitch=60,
            start_beat=0,
            duration_beats=4,
            velocity=76,
            channel=0,
            chord_label="Cm7",
        )

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
                events=[event],
            )
        ],
    )


def assert_has_error_field(plan: ChordMidiPlan, field: str) -> None:
    result = validate_chord_midi_plan(plan)

    assert not result.is_valid
    assert any(error.field == field for error in result.errors)


def test_valid_chord_midi_plan_passes():
    result = validate_chord_midi_plan(make_valid_plan())

    assert result.is_valid
    assert result.errors == []


def test_invalid_pitch_fails():
    event = replace(make_valid_plan().tracks[0].events[0], pitch=128)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].pitch")


def test_invalid_velocity_fails():
    event = replace(make_valid_plan().tracks[0].events[0], velocity=128)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].velocity")


def test_invalid_channel_fails():
    event = replace(make_valid_plan().tracks[0].events[0], channel=16)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].channel")


def test_negative_start_beat_fails():
    event = replace(make_valid_plan().tracks[0].events[0], start_beat=-0.25)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].start_beat")


def test_zero_duration_fails():
    event = replace(make_valid_plan().tracks[0].events[0], duration_beats=0)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].duration_beats")


def test_off_grid_start_beat_fails():
    event = replace(make_valid_plan().tracks[0].events[0], start_beat=0.1)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].start_beat")


def test_event_extending_past_total_bars_fails():
    event = replace(make_valid_plan().tracks[0].events[0], start_beat=3, duration_beats=2)

    assert_has_error_field(make_valid_plan(event), "tracks[0].events[0].duration_beats")

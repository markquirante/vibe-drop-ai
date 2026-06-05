from mido import MidiFile

from vibedrop_ai.domain import ChordMidiPlan, ChordNoteEvent, ChordTrackPlan
from vibedrop_ai.generation_service import generate_from_plan


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


def test_generate_from_plan_renders_explicit_note_events(tmp_path):
    output_path = tmp_path / "idea.mid"

    generate_from_plan(make_valid_plan(), output_path)

    midi = MidiFile(output_path)
    messages = [
        message
        for track in midi.tracks
        for message in track
        if message.type in {"note_on", "note_off"}
    ]

    assert [(message.type, message.note, message.velocity) for message in messages] == [
        ("note_on", 60, 76),
        ("note_on", 63, 72),
        ("note_off", 60, 0),
        ("note_off", 63, 0),
    ]


def test_generate_from_plan_is_deterministic_for_same_event_plan(tmp_path):
    plan = make_valid_plan()
    first_path = tmp_path / "first.mid"
    second_path = tmp_path / "second.mid"

    generate_from_plan(plan, first_path)
    generate_from_plan(plan, second_path)

    assert first_path.read_bytes() == second_path.read_bytes()

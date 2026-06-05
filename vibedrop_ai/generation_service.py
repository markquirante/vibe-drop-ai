from pathlib import Path

from mido import MidiFile

from vibedrop_ai.config import TICKS_PER_BEAT
from vibedrop_ai.domain import ChordMidiPlan, GeneratedArtifact
from vibedrop_ai.music.midi_io import write_chord_midi_plan
from vibedrop_ai.validation.chord_midi import validate_chord_midi_plan


def generate_from_plan(plan: ChordMidiPlan, output_path: Path) -> GeneratedArtifact:
    validation = validate_chord_midi_plan(plan)
    if not validation.is_valid:
        messages = [f"{error.field}: {error.message}" for error in validation.errors]
        raise ValueError("Invalid chord MIDI plan: " + "; ".join(messages))

    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    write_chord_midi_plan(
        mid=mid,
        plan=plan,
        ticks_per_quarter=TICKS_PER_BEAT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(output_path)

    return GeneratedArtifact(
        path=output_path,
        plan=plan,
    )

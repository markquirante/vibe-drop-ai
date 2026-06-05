import random
from pathlib import Path

from mido import MidiFile

from vibedrop_ai.config import DEFAULT_TIME_SIGNATURE, TICKS_PER_BEAT
from vibedrop_ai.domain import CompositionPlan, GeneratedArtifact
from vibedrop_ai.generators.chord_engine import generate_cm_chord_prog
from vibedrop_ai.music.midi_io import write_chord_track
from vibedrop_ai.validation.music_theory import validate_composition_plan


def generate_from_plan(plan: CompositionPlan, output_path: Path) -> GeneratedArtifact:
    validation = validate_composition_plan(plan)
    if not validation.is_valid:
        messages = [f"{error.field}: {error.message}" for error in validation.errors]
        raise ValueError("Invalid composition plan: " + "; ".join(messages))

    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)

    rng = random.Random(plan.seed)
    chords = generate_cm_chord_prog(bars=plan.bars, rng=rng)
    write_chord_track(
        mid=mid,
        chords=chords,
        ts=DEFAULT_TIME_SIGNATURE,
        ticks_per_quarter=TICKS_PER_BEAT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(output_path)

    return GeneratedArtifact(
        path=output_path,
        plan=plan,
    )

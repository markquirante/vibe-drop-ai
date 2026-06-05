import random
from dataclasses import dataclass
from vibedrop_ai.config import ROOT_NOTE

@dataclass
class ChordEvent:
    start_bar: float
    duration_bars: float
    notes: list[int]

# chords
def _cm7() -> list[int]:
    return [ROOT_NOTE + i for i in (0, 3, 7, 10)]

def _ddimb5() -> list[int]:
    return [ROOT_NOTE + i for i in (2, 5, 8, 12)]

def _emaj7() -> list[int]:
    return [ROOT_NOTE + i for i in (3, 7, 10, 14)]

def _fm7() -> list[int]:
    return [ROOT_NOTE + i for i in (5, 8, 12, 15)]

def _gm7() -> list[int]:
    return [ROOT_NOTE + i for i in (7, 10, 14, 17)]

def _abmaj7() -> list[int]:
    return [ROOT_NOTE + i for i in (8, 12, 15, 19)]

def _bb7() -> list[int]:
    return [ROOT_NOTE + i for i in (10, 14, 17, 20)]

CHORD_POOL = [
    _cm7(),
    _ddimb5(),
    _emaj7(),
    _fm7(),
    _gm7(),
    _abmaj7(),
    _bb7(),
]

# generate chord progression
def generate_cm_chord_prog(
    bars: int,
    rng: random.Random | None = None,
) -> list[ChordEvent]:
    if rng is None:
        rng = random.Random()

    events: list[ChordEvent] = []
    for bar_index in range(bars):
        chord_notes = rng.choice(CHORD_POOL)

        events.append(
            ChordEvent(
                start_bar=bar_index,
                duration_bars=1,
                notes=chord_notes,
            )
        )

    return events

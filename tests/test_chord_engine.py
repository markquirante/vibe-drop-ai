import random

from vibedrop_ai.generators.chord_engine import ChordEvent, generate_cm_chord_prog


def test_generate_cm_chord_prog_is_repeatable_with_same_seed():
    first = generate_cm_chord_prog(bars=4, rng=random.Random(123))
    second = generate_cm_chord_prog(bars=4, rng=random.Random(123))

    assert first == second


def test_generate_cm_chord_prog_uses_requested_bar_count():
    events = generate_cm_chord_prog(bars=4, rng=random.Random(123))

    assert len(events) == 4
    assert [event.start_bar for event in events] == [0, 1, 2, 3]
    assert all(event.duration_bars == 1 for event in events)
    assert all(isinstance(event, ChordEvent) for event in events)

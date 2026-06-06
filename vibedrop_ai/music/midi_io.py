from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from vibedrop_ai.generators.chord_engine import ChordEvent
from vibedrop_ai.domain import ChordMidiPlan, ChordTrackPlan
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSignature:
    numerator: int
    denominator: int


TICKS_PER_BEAT = 480

def beats_to_ticks(beats, ts: TimeSignature, ticks_per_quarter):
    quarter_notes_per_beat = 4 / ts.denominator
    return int(beats * quarter_notes_per_beat * ticks_per_quarter)


def bars_to_ticks(bars, ts: TimeSignature, ticks_per_quarter):
    total_beats = bars * ts.numerator
    return beats_to_ticks(total_beats, ts, ticks_per_quarter)


def write_chord_midi_plan(
    mid: MidiFile,
    plan: ChordMidiPlan,
    ticks_per_quarter: int,
) -> None:
    ts = TimeSignature(
        numerator=plan.time_signature_numerator,
        denominator=plan.time_signature_denominator,
    )

    for index, track_plan in enumerate(plan.tracks):
        write_chord_note_track(
            mid=mid,
            track_plan=track_plan,
            ts=ts,
            ticks_per_quarter=ticks_per_quarter,
            tempo_bpm=plan.tempo_bpm if index == 0 else None,
        )


def write_chord_note_track(
    mid: MidiFile,
    track_plan: ChordTrackPlan,
    ts: TimeSignature,
    ticks_per_quarter: int,
    tempo_bpm: int | None = None,
) -> None:
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name=track_plan.name, time=0))

    if tempo_bpm is not None:
        track.append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo_bpm), time=0))
        track.append(
            MetaMessage(
                "time_signature",
                numerator=ts.numerator,
                denominator=ts.denominator,
                time=0,
            )
        )

    timed_messages = []
    for index, event in enumerate(track_plan.events):
        start_tick = beats_to_ticks(event.start_beat, ts, ticks_per_quarter)
        duration_ticks = beats_to_ticks(event.duration_beats, ts, ticks_per_quarter)
        end_tick = start_tick + duration_ticks

        timed_messages.append(
            (
                start_tick,
                1,
                event.pitch,
                event.channel,
                index,
                Message(
                    "note_on",
                    note=event.pitch,
                    velocity=event.velocity,
                    channel=event.channel,
                    time=0,
                ),
            )
        )
        timed_messages.append(
            (
                end_tick,
                0,
                event.pitch,
                event.channel,
                index,
                Message(
                    "note_off",
                    note=event.pitch,
                    velocity=0,
                    channel=event.channel,
                    time=0,
                ),
            )
        )

    last_tick = 0
    for tick, _, _, _, _, message in sorted(timed_messages):
        message.time = tick - last_tick
        track.append(message)
        last_tick = tick


def write_chord_track(
    mid: MidiFile,
    chords: list[ChordEvent],
    ts,
    ticks_per_quarter: int,
) -> None:
    track = MidiTrack()
    mid.tracks.append(track)

    chords = sorted(chords, key=lambda ev: ev.start_bar)

    last_tick = 0
    for event in chords:
        chord_start_ticks = bars_to_ticks(event.start_bar, ts, ticks_per_quarter)
        chord_duration_ticks = bars_to_ticks(event.duration_bars, ts, ticks_per_quarter)

        delta = chord_start_ticks - last_tick
        if delta < 0:
            delta = 0

        # NOTE ONs
        for i, note in enumerate(event.notes):
            time = delta if i == 0 else 0
            track.append(Message("note_on", note=note, velocity=80, time=time))

        # NOTE OFFs
        for i, note in enumerate(event.notes):
            time = chord_duration_ticks if i == 0 else 0
            track.append(Message("note_off", note=note, velocity=0, time=time))

        last_tick = chord_start_ticks + chord_duration_ticks

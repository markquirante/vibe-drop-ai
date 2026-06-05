import json
from pathlib import Path

from vibedrop_ai.domain import CompositionPlan, TrackSpec, ChordMidiPlan, ChordNoteEvent, ChordTrackPlan

def load_composition_plan(path: Path) -> CompositionPlan:
    data = json.loads(path.read_text())

    tracks = [
        TrackSpec(
            role=track["role"],
            channel=track["channel"],
        )
        for track in data["tracks"]
    ]

    return CompositionPlan(
        key=data["key"],
        scale=data["scale"],
        tempo_bpm=data["tempo_bpm"],
        bars=data["bars"],
        style=data["style"],
        tracks=tracks,
        seed=data.get("seed"),
    )

def load_chord_midi_plan(path: Path) -> ChordMidiPlan:
    data = json.loads(path.read_text())

    time_signature = data.get("time_signature", {})

    tracks = []
    for track_data in data["tracks"]:
        track_channel = track_data.get("channel", 0)

        events = [
            ChordNoteEvent(
                pitch=event["pitch"],
                start_beat=event["start_beat"],
                duration_beats=event["duration_beats"],
                velocity=event.get("velocity", 80),
                channel=event.get("channel", track_channel),
                chord_label=event.get("chord_label"),
            )
            for event in track_data.get("events", [])
        ]

        tracks.append(
            ChordTrackPlan(
                name=track_data["name"],
                channel=track_channel,
                events=events,
            )
        )

    return ChordMidiPlan(
        key=data["key"],
        scale=data["scale"],
        tempo_bpm=data["tempo_bpm"],
        bars=data["bars"],
        style=data["style"],
        time_signature_numerator=time_signature.get("numerator", 4),
        time_signature_denominator=time_signature.get("denominator", 4),
        tracks=tracks,
    )

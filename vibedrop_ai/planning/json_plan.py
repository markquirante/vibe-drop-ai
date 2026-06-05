import json
from pathlib import Path

from vibedrop_ai.domain import CompositionPlan, TrackSpec

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
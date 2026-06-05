from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class ChordNoteEvent:
    pitch: int
    start_beat: float
    duration_beats: float
    velocity: int = 80
    channel: int = 0
    chord_label: str | None = None

@dataclass(frozen=True)
class ChordTrackPlan:
    name: str
    channel: int
    events: list[ChordNoteEvent] = field(default_factory=list)

@dataclass(frozen=True)
class ChordMidiPlan:
    key: str
    scale: str
    tempo_bpm: int
    bars: int
    style: str
    tracks: list[ChordTrackPlan] = field(default_factory=list)
    time_signature_numerator: int = 4
    time_signature_denominator: int = 4

@dataclass(frozen=True)
class TrackSpec:
    role: str
    channel: int = 0

@dataclass(frozen=True)
class CompositionPlan:
    key: str
    scale: str
    tempo_bpm: int
    bars: int
    style: str
    tracks: list[TrackSpec]
    seed: int | None = None

@dataclass(frozen=True)
class ValidationIssue:
    field: str
    message: str

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]

@dataclass(frozen=True)
class GeneratedArtifact:
    path: Path
    plan: CompositionPlan | ChordMidiPlan

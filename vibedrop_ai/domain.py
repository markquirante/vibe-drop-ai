from dataclasses import dataclass
from pathlib import Path

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
    plan: CompositionPlan
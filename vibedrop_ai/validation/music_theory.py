from vibedrop_ai.domain import CompositionPlan, ValidationResult, ValidationIssue

SUPPORTED_KEYS = {"C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"}
SUPPORTED_SCALES = {"major", "minor"}
SUPPORTED_STYLES = {"lofi", "rnb"}
SUPPORTED_TRACK_ROLES = {"chords"}

MIN_TEMPO_BPM = 40
MAX_TEMPO_BPM = 220
MIN_BARS = 1
MAX_BARS = 64
MIN_MIDI_CHANNEL = 0
MAX_MIDI_CHANNEL = 15

def validate_composition_plan(plan: CompositionPlan) -> ValidationResult:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if plan.key not in SUPPORTED_KEYS:
        errors.append(
            ValidationIssue(
                field="key",
                message=f"Key must be one of: {SUPPORTED_KEYS}",
            )
        )

    if plan.scale not in SUPPORTED_SCALES:
        errors.append(
            ValidationIssue(
                field="scale",
                message=f"scale must be one of: {SUPPORTED_SCALES}",
            )
        )

    if not MIN_TEMPO_BPM <= plan.tempo_bpm <= MAX_TEMPO_BPM:
        errors.append(
            ValidationIssue(
                field="tempo_bpm",
                message=f"Tempo must be between {MIN_TEMPO_BPM} and {MAX_TEMPO_BPM}",
            )
        )

    if not MIN_BARS <= plan.bars <= MAX_BARS:
        errors.append(
            ValidationIssue(
                field="bars",
                message=f"Bars must be between {MIN_BARS} and {MAX_BARS}",
            )
        )

    if plan.style not in SUPPORTED_STYLES:
        errors.append(
            ValidationIssue(
                field="style",
                message=f"style must be one of: {SUPPORTED_STYLES}",
            )
        )

    if not plan.tracks:
        errors.append(
            ValidationIssue(
                field="tracks",
                message=f"At least one track is required",
            )
        )

    seen_roles: set[str] = set()
    seen_channels: set[int] = set()

    for index, track in enumerate(plan.tracks):

        if track.role not in SUPPORTED_TRACK_ROLES:
            errors.append(
                ValidationIssue(
                    field=f"tracks[{index}].role",
                    message=f"Track must be one of {SUPPORTED_TRACK_ROLES}",
                )
            )

        if track.role in seen_roles:
            errors.append(
                ValidationIssue(
                    field=f"tracks[{index}].role",
                    message=f"Duplicate track role: {track.role}",
                )
            )
        seen_roles.add(track.role)

        if not MIN_MIDI_CHANNEL <= track.channel <= MAX_MIDI_CHANNEL:
            errors.append(
                ValidationIssue(
                    field=f"tracks[{index}].channel",
                    message=f"MIDI channel must be between {MIN_MIDI_CHANNEL} and {MAX_MIDI_CHANNEL}",
                )
            )

        if track.channel in seen_channels:
            errors.append(
                ValidationIssue(
                    field=f"tracks[{index}].channel",
                    message=f"Duplicate MIDI channel: {track.channel}",
                )
            )
        seen_channels.add(track.channel)

    if plan.seed is not None and plan.seed < 0:
        errors.append(
            ValidationIssue(
                field="seed",
                message=f"Seed must be 0 or higher",
            )
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

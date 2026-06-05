from vibedrop_ai.domain import ChordMidiPlan, ValidationIssue, ValidationResult

SUPPORTED_KEYS = {"C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"}
SUPPORTED_SCALES = {"major", "minor"}
SUPPORTED_STYLES = {"lofi", "rnb"}

MIN_TEMPO_BPM = 40
MAX_TEMPO_BPM = 220
MIN_BARS = 1
MAX_BARS = 64
MIN_MIDI_VALUE = 0
MAX_MIDI_VALUE = 127
MIN_MIDI_CHANNEL = 0
MAX_MIDI_CHANNEL = 15
SUPPORTED_GRID_BEATS = 0.25
GRID_TOLERANCE = 1e-9


def is_on_grid(value: float, grid: float = SUPPORTED_GRID_BEATS) -> bool:
    return abs(round(value / grid) * grid - value) < GRID_TOLERANCE


def validate_chord_midi_plan(plan: ChordMidiPlan) -> ValidationResult:
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
                message=f"Scale must be one of: {SUPPORTED_SCALES}",
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
                message=f"Style must be one of: {SUPPORTED_STYLES}",
            )
        )

    if plan.time_signature_numerator <= 0:
        errors.append(
            ValidationIssue(
                field="time_signature_numerator",
                message="Time signature numerator must be positive",
            )
        )

    if plan.time_signature_denominator <= 0:
        errors.append(
            ValidationIssue(
                field="time_signature_denominator",
                message="Time signature denominator must be positive",
            )
        )

    if not plan.tracks:
        errors.append(
            ValidationIssue(
                field="tracks",
                message="At least one chord track is required",
            )
        )

    total_beats = plan.bars * plan.time_signature_numerator

    for track_index, track in enumerate(plan.tracks):
        track_field = f"tracks[{track_index}]"

        if not track.name.strip():
            errors.append(
                ValidationIssue(
                    field=f"{track_field}.name",
                    message="Track name must not be empty",
                )
            )

        if not MIN_MIDI_CHANNEL <= track.channel <= MAX_MIDI_CHANNEL:
            errors.append(
                ValidationIssue(
                    field=f"{track_field}.channel",
                    message=f"MIDI channel must be between {MIN_MIDI_CHANNEL} and {MAX_MIDI_CHANNEL}",
                )
            )

        if not track.events:
            errors.append(
                ValidationIssue(
                    field=f"{track_field}.events",
                    message="At least one chord note event is required",
                )
            )

        for event_index, event in enumerate(track.events):
            event_field = f"{track_field}.events[{event_index}]"

            if not MIN_MIDI_VALUE <= event.pitch <= MAX_MIDI_VALUE:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.pitch",
                        message=f"Pitch must be between {MIN_MIDI_VALUE} and {MAX_MIDI_VALUE}",
                    )
                )

            if not MIN_MIDI_VALUE <= event.velocity <= MAX_MIDI_VALUE:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.velocity",
                        message=f"Velocity must be between {MIN_MIDI_VALUE} and {MAX_MIDI_VALUE}",
                    )
                )

            if not MIN_MIDI_CHANNEL <= event.channel <= MAX_MIDI_CHANNEL:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.channel",
                        message=f"MIDI channel must be between {MIN_MIDI_CHANNEL} and {MAX_MIDI_CHANNEL}",
                    )
                )

            if event.start_beat < 0:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.start_beat",
                        message="Start beat must not be negative",
                    )
                )

            if not is_on_grid(event.start_beat):
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.start_beat",
                        message=f"Start beat must land on a {SUPPORTED_GRID_BEATS}-beat grid",
                    )
                )

            if event.duration_beats <= 0:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.duration_beats",
                        message="Duration beats must be positive",
                    )
                )

            if event.start_beat + event.duration_beats > total_beats:
                errors.append(
                    ValidationIssue(
                        field=f"{event_field}.duration_beats",
                        message="Note event must fit within the total plan length",
                    )
                )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )

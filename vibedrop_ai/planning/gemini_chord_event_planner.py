import json
import os
import urllib.error
import urllib.request
from typing import Any

from vibedrop_ai.domain import ChordMidiPlan, ChordNoteEvent, ChordTrackPlan
from vibedrop_ai.planning.chord_event_planner import (
    ChordEventPlannerRequest,
    PlannerUnavailableError,
)

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

CHORD_MIDI_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "key": {
            "type": "string",
            "enum": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
        },
        "scale": {
            "type": "string",
            "enum": ["major", "minor"],
        },
        "tempo_bpm": {
            "type": "integer",
            "minimum": 40,
            "maximum": 220,
        },
        "bars": {
            "type": "integer",
            "minimum": 1,
            "maximum": 64,
        },
        "style": {
            "type": "string",
            "enum": ["lofi", "rnb"],
        },
        "time_signature": {
            "type": "object",
            "properties": {
                "numerator": {"type": "integer", "minimum": 1},
                "denominator": {"type": "integer", "minimum": 1},
            },
            "required": ["numerator", "denominator"],
        },
        "tracks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "channel": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 15,
                    },
                    "events": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "properties": {
                                "pitch": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 127,
                                },
                                "start_beat": {
                                    "type": "number",
                                    "minimum": 0,
                                },
                                "duration_beats": {
                                    "type": "number",
                                    "minimum": 0.25,
                                },
                                "velocity": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 127,
                                },
                                "channel": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 15,
                                },
                                "chord_label": {
                                    "type": ["string", "null"],
                                },
                            },
                            "required": [
                                "pitch",
                                "start_beat",
                                "duration_beats",
                                "velocity",
                                "channel",
                            ],
                        },
                    },
                },
                "required": ["name", "channel", "events"],
            },
        },
    },
    "required": [
        "key",
        "scale",
        "tempo_bpm",
        "bars",
        "style",
        "time_signature",
        "tracks",
    ],
}


class GeminiPlannerError(RuntimeError):
    pass


class GeminiChordEventPlanner:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def plan_from_prompt(self, request: ChordEventPlannerRequest) -> ChordMidiPlan:
        if not self.api_key:
            raise PlannerUnavailableError("GEMINI_API_KEY is not set")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": _build_prompt(request),
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": CHORD_MIDI_PLAN_SCHEMA,
                "temperature": 0.8,
            },
        }

        response_data = self._post_json(payload)
        text = _extract_response_text(response_data)
        plan_data = json.loads(text)
        return chord_midi_plan_from_dict(plan_data)

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = GEMINI_API_URL.format(model=self.model)
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key or "",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise GeminiPlannerError(f"Gemini API request failed: {error.code} {details}") from error
        except urllib.error.URLError as error:
            raise GeminiPlannerError(f"Gemini API request failed: {error.reason}") from error


def chord_midi_plan_from_dict(data: dict[str, Any]) -> ChordMidiPlan:
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
        tracks=tracks,
        time_signature_numerator=time_signature.get("numerator", 4),
        time_signature_denominator=time_signature.get("denominator", 4),
    )


def _extract_response_text(response_data: dict[str, Any]) -> str:
    try:
        return response_data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as error:
        raise GeminiPlannerError("Gemini API response did not include response text") from error


def _build_prompt(request: ChordEventPlannerRequest) -> str:
    constraints = []
    if request.key:
        constraints.append(f"key: {request.key}")
    if request.scale:
        constraints.append(f"scale: {request.scale}")
    if request.tempo_bpm:
        constraints.append(f"tempo_bpm: {request.tempo_bpm}")
    if request.bars:
        constraints.append(f"bars: {request.bars}")
    if request.style:
        constraints.append(f"style: {request.style}")

    constraint_text = "\n".join(f"- {constraint}" for constraint in constraints)
    if not constraint_text:
        constraint_text = "- infer suitable values from the prompt"

    return f"""
Create an AI-authored chord MIDI event plan for Vibe Drop AI.

User prompt:
{request.prompt}

Constraints:
{constraint_text}

Rules:
- Return only a structured chord MIDI plan matching the provided schema.
- Do not include melody, drums, bass, vocals, or raw MIDI bytes.
- Use one chord track unless the prompt clearly asks for layered chord tracks.
- Use absolute beat timing where beat 0 is the start of the loop.
- Use a 0.25 beat timing grid.
- Ensure every note fits inside bars * time_signature.numerator beats.
- Use MIDI pitches, velocities, and channels only.
- Chord labels are optional metadata; rendered notes are the source of truth.
""".strip()

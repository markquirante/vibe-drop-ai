import argparse
from pathlib import Path

from vibedrop_ai.generation_service import generate_from_prompt
from vibedrop_ai.planning.chord_event_planner import ChordEventPlannerRequest
from vibedrop_ai.planning.gemini_chord_event_planner import (
    DEFAULT_GEMINI_MODEL,
    GeminiChordEventPlanner,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a chord MIDI file from a prompt using Gemini."
    )
    parser.add_argument("prompt", help="Prompt describing the chord loop to generate.")
    parser.add_argument("output_path", type=Path, help="Path where the MIDI file should be saved.")
    parser.add_argument("--key", help="Optional musical key, e.g. C or Ab.")
    parser.add_argument("--scale", choices=["major", "minor"], help="Optional scale.")
    parser.add_argument("--tempo-bpm", type=int, help="Optional tempo in BPM.")
    parser.add_argument("--bars", type=int, help="Optional number of bars.")
    parser.add_argument("--style", choices=["lofi", "rnb"], help="Optional style.")
    parser.add_argument(
        "--model",
        default=DEFAULT_GEMINI_MODEL,
        help=f"Gemini model to use. Defaults to {DEFAULT_GEMINI_MODEL}.",
    )
    parser.add_argument(
        "--plan-output-path",
        type=Path,
        help="Optional path for the generated JSON chord event plan.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    request = ChordEventPlannerRequest(
        prompt=args.prompt,
        key=args.key,
        scale=args.scale,
        tempo_bpm=args.tempo_bpm,
        bars=args.bars,
        style=args.style,
    )
    planner = GeminiChordEventPlanner(model=args.model)
    plan_output_path = args.plan_output_path or args.output_path.with_suffix(".plan.json")

    artifact = generate_from_prompt(
        request=request,
        output_path=args.output_path,
        planner=planner,
        plan_output_path=plan_output_path,
    )

    print(f"Saved MIDI: {artifact.path}")
    print(f"Saved plan: {plan_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

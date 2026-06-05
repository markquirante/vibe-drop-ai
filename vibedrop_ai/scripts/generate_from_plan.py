import argparse
from pathlib import Path

from vibedrop_ai.generation_service import generate_from_plan
from vibedrop_ai.planning.json_plan import load_composition_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a MIDI file from a local JSON composition plan."
    )
    parser.add_argument("plan_path", type=Path, help="Path to a JSON composition plan.")
    parser.add_argument("output_path", type=Path, help="Path where the MIDI file should be saved.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plan = load_composition_plan(args.plan_path)
    artifact = generate_from_plan(plan, args.output_path)

    print(f"Saved: {artifact.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Vibe Drop AI

Vibe Drop AI is an AI-assisted producer asset generator for creating validated, DAW-ready chord MIDI files.

The project turns structured musical ideas into reliable MIDI assets. Instead of asking AI to generate raw `.mid` binary files, Vibe Drop AI uses AI or local JSON plans to describe chord note events, then validates and renders those events deterministically.

## What It Does

```text
Prompt or JSON chord event plan
-> validated chord MIDI event data
-> deterministic MIDI rendering
-> DAW-ready .mid file
```

## Current Focus

- AI-authored chord MIDI event plans.
- Hand-written JSON chord event plans.
- Validation for MIDI pitch, velocity, channel, timing, duration, beat-grid alignment, and loop length.
- Deterministic `.mid` file rendering through `mido`.
- Saved chord event plans for inspection and reproducibility.

## Product Direction

Vibe Drop AI is focused on producer-ready musical assets:

- Chord MIDI files first.
- Drum-loop audio packages later.
- Master loops and separated stems later.

Melody generation is not part of the supported product path.

## Design Principle

AI is allowed to make creative musical decisions such as chord choices, voicings, timing, durations, and velocities.

Vibe Drop AI is responsible for validation, safety checks, deterministic rendering, and producing files that can be used in a DAW.

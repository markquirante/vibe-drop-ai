# AI Roadmap

## Direction

Vibe Drop AI should evolve into an AI-assisted producer asset generator with two focused outputs:

1. AI-authored chord MIDI files.
2. AI-generated finished drum-loop audio packages with a master loop and separated stems.

The app should not generate melodies.

For chord MIDI, the AI should create the musical content directly as structured MIDI-ready events. That means the AI chooses the chord notes, voicings, timing, durations, velocities, and optional chord labels. Vibe Drop AI should not use rule-based chord generation as the primary composer.

The app still should not ask an LLM to produce raw `.mid` binary data. The safer architecture is:

```text
User prompt
  -> AI chord event planner
  -> structured chord MIDI event plan
  -> validation and repair
  -> deterministic MIDI file writer
  -> .mid file
```

For drums:

```text
User prompt
  -> Lyria 3 drum-loop prompt via Gemini API generateContent
  -> generated drum-loop audio
  -> validation and packaging
  -> master.wav plus stems
```

## Product Scope

### In Scope

- AI-authored chord MIDI event generation.
- Deterministic writing of valid `.mid` files from AI-authored events.
- Validation for MIDI note range, timing, duration, velocity, channel, bar length, and optional music-theory constraints.
- AI-generated finished drum loops as audio.
- Lyria 3 through Gemini API `generateContent` as the first external audio-generation path for drum loops only.
- Drum-loop master export.
- Drum-loop stem export:
  - kick
  - snare
  - hi-hats
  - percussion
  - optional extra layers later
- Dataset preparation for chord MIDI event plans and drum-loop assets.
- Eventually, retrieval or small ML models for chord events and drum patterns/assets.

### Out of Scope

- Melody generation.
- AI-generated melodies.
- Raw `.mid` binary generation by an LLM.
- Full song arrangement generation.
- Vocal generation.
- Lyria 3 usage for non-drum full songs, vocals, melodies, or general music arrangement.
- Full mixing/mastering suites.
- Real-time plugin generation.
- Custom ML before stable schemas, validation, rendering, and dataset utilities exist.

## Alignment With Current Repository

The current repository has useful infrastructure but needs a direction adjustment:

- `vibedrop_ai/music/midi_io.py` is still useful as the deterministic MIDI writer layer.
- `vibedrop_ai/config.py` is still useful for timing defaults.
- `vibedrop_ai/domain.py`, `planning/json_plan.py`, `validation/music_theory.py`, and `generation_service.py` are early versions of the plan/validate/render boundary.
- `vibedrop_ai/generators/chord_engine.py` should become a fallback/dev baseline, not the main chord composer.
- Melody-oriented files should be retired or de-emphasized:
  - `vibedrop_ai/generators/poc_melody.py`
  - `vibedrop_ai/generators/melody_engine.py`
  - `vibedrop_ai/scripts/generate_midi.py`
  - `melody` as a supported track role

The new chord path should accept AI-authored note events instead of asking rule-based code to choose the chords.

## Existing Code To Preserve

Preserve:

- MIDI writing with `mido`.
- Bar/beat/tick timing.
- Validation result patterns.
- JSON plan loading as a non-AI test path.
- Output artifact conventions.
- Existing tests where they still apply to validation and MIDI writing.

Preserve the rule-based chord generator only as:

- a fallback when AI is unavailable,
- a development smoke test,
- a baseline for comparison.

## Existing Code To Retire Or Change

Retire or change:

- Remove melody from supported product scope.
- Remove `melody` from valid track roles.
- Replace generic `CompositionPlan` naming with a chord-specific event plan before adding drum types.
- Replace random chord generation as the primary generation path.
- Update sample plans so they contain AI-style chord note events, not melody tracks.

## New Abstractions Needed

### Chord MIDI

- `ChordMidiPlan`
  - key, scale, tempo, bars, time signature, style, track metadata, and chord note events.

- `ChordNoteEvent`
  - pitch, start beat, duration beats, velocity, channel, optional chord label.

- `ChordTrackPlan`
  - one chord track containing note events and MIDI channel settings.

- `MidiValidationResult`
  - validation errors and warnings for MIDI event plans.

- `MidiRenderContext`
  - ticks per beat, time signature, tempo, output path, track name.

### Drum Audio

- `DrumLoopRequest`
  - prompt, style, BPM, bars, swing, energy, density, requested stems, Lyria model.

- `DrumLoopPlan`
  - planned drum elements, loop length, stem roles, groove notes, generation strategy, provider metadata.

- `DrumStemSpec`
  - stem name, role, audio source/generation source, output path.

- `DrumLoopPackage`
  - master audio path, stem paths, metadata, BPM, bars, sample rate.

- `AudioRenderContext`
  - sample rate, bit depth, channels, output format, loop length, normalization policy.

## Phase 1: AI Chord MIDI Event Planner

### Objective

Let AI generate structured chord MIDI event plans. The app validates those events and writes a valid MIDI file.

The app is not composing the chords in this phase. It is validating and exporting the AI-authored event plan.

### Deliverables

- `ChordMidiPlan` schema.
- `ChordNoteEvent` schema.
- JSON chord event plan input path.
- Prompt-to-chord-event-plan interface.
- MIDI event validation:
  - pitch 0-127
  - velocity 0-127
  - channel 0-15
  - positive duration
  - starts on supported grid
  - notes fit within total bars
  - no impossible negative timing
- Deterministic `.mid` writer from validated events.
- Tests for validation and MIDI writing.

### Required Architecture Changes

- Stop using rule-based chord generation as the main Phase 1 path.
- Keep `mido` as the file writer.
- Split "AI-authored event plan" from "MIDI file writing."
- Rename generic composition concepts toward chord MIDI event concepts.
- Remove melody from validation and plans.

### Suggested Modules/Files

- `vibedrop_ai/domain.py`
- `vibedrop_ai/planning/chord_event_planner.py`
- `vibedrop_ai/planning/json_plan.py`
- `vibedrop_ai/validation/chord_midi.py`
- `vibedrop_ai/music/midi_io.py`
- `vibedrop_ai/generation_service.py`
- `vibedrop_ai/scripts/generate_from_plan.py`
- `plans/lofi_c_minor.json`
- `tests/test_chord_midi_validation.py`
- `tests/test_chord_midi_rendering.py`

### AI Concepts Learned

- Structured LLM output.
- Prompt-to-event planning.
- Constrained symbolic generation.
- Validation of nondeterministic AI output.
- Repair loops for invalid event plans.

### Software Engineering Concepts Learned

- Domain modeling.
- Boundary design between AI and deterministic code.
- File format export.
- Validation pipelines.
- Testable data contracts.

### Risks

- AI may output malformed JSON.
- AI may create invalid MIDI events.
- AI may produce musically weak but technically valid chords.
- Validation may reject creative but unusual voicings.
- The project may accidentally keep old rule-based composition assumptions.

### Success Criteria

- A hand-written JSON event plan renders to a valid `.mid`.
- An AI-authored event plan can render after validation.
- Invalid pitch, timing, velocity, channel, and duration values are rejected.
- The `.mid` file writer is deterministic for the same event plan.
- Melody is no longer part of the supported path.

### Suggested First Implementation Tasks

- Define `ChordMidiPlan` and `ChordNoteEvent`.
- Create a hand-written chord event JSON file.
- Validate the hand-written event plan.
- Render the hand-written event plan to MIDI.
- Only then add an AI planner that outputs the same JSON shape.

## Phase 2: Chord Quality, Repair, And Musical Validation

### Objective

Improve the quality and safety of AI-authored chord event plans with stronger validation, optional chord-label metadata, repair logic, and music-theory checks.

### Deliverables

- Optional chord label metadata such as `Cm7`, `Fm9`, `Abmaj7`.
- Chord-label validation against note events.
- Voicing range checks.
- Maximum hand-span or playability checks.
- Duplicate note handling.
- Timing overlap checks.
- Repair suggestions for common AI mistakes.
- Tests for chord-label and event repair behavior.

### Required Architecture Changes

- Treat MIDI note events as the source of truth.
- Treat chord symbols as metadata, not the render source.
- Add music-theory validation without taking composition control away from the AI.

### Suggested Modules/Files

- `vibedrop_ai/validation/chord_midi.py`
- `vibedrop_ai/music/chord_labels.py`
- `vibedrop_ai/music/theory.py`
- `tests/test_chord_label_validation.py`
- `tests/test_chord_event_repair.py`

### AI Concepts Learned

- AI self-repair.
- Constrained retry prompts.
- Symbolic music evaluation.
- Separating musical metadata from renderable events.

### Software Engineering Concepts Learned

- Validation layering.
- Repair strategies.
- Domain-specific invariants.
- Regression testing generated structures.

### Risks

- Repair logic can become too complex.
- Chord-label validation can be ambiguous.
- Strong theory validation may reject genre-appropriate dissonance.

### Success Criteria

- AI can output richer chord event plans.
- The app catches and explains invalid event plans.
- Optional repair can turn common invalid plans into valid MIDI.
- The rendered MIDI remains based on AI-authored notes, not rule-generated chords.

## Phase 3: AI Drum Loop Audio Generator

### Objective

Add AI-assisted generation of finished drum loops as audio files. The first provider path should use Lyria 3 through Gemini API `generateContent`, scoped exclusively to drum-loop audio. Each loop should include a master file and separated stems where feasible.

### Deliverables

- Drum-loop request schema.
- Drum-loop plan or generation result schema.
- Lyria 3 `generateContent` client for drum-loop prompts.
- Provider metadata recording:
  - model ID
  - prompt
  - generated audio format
  - generation timestamp
- Stem roles:
  - kick
  - snare
  - hats
  - percussion
  - optional fills
- Drum-loop package:
  - `master.wav`
  - `kick.wav`
  - `snare.wav`
  - `hats.wav`
  - `percussion.wav`
  - `metadata.json`
- Stem/master alignment validation.
- Loop-length validation.

### Required Architecture Changes

- Add an audio package layer separate from MIDI.
- Add drum-specific validation.
- Use Lyria 3 as the first AI-audio-model provider for drum-loop master generation.
- Keep stem handling separate from Lyria 3 master generation because provider output may not include isolated stems.
- Preserve a future hybrid option for stem generation, separation, or sample-based reconstruction.
- Track loop duration in bars, beats, seconds, and samples.

### Suggested Modules/Files

- `vibedrop_ai/drums/domain.py`
- `vibedrop_ai/drums/planner.py`
- `vibedrop_ai/drums/lyria_client.py`
- `vibedrop_ai/audio/render.py`
- `vibedrop_ai/audio/stems.py`
- `vibedrop_ai/validation/drums.py`
- `vibedrop_ai/scripts/generate_drum_loop.py`
- `tests/test_drum_loop_package.py`

### AI Concepts Learned

- Prompt-to-audio asset planning.
- Gemini API media generation through Lyria 3.
- Stem-aware generation.
- Audio generation constraints.
- AI-assisted production workflow design.

### Software Engineering Concepts Learned

- Multi-file artifact packaging.
- Audio metadata.
- Stem alignment.
- File conventions.
- Validation across related files.

### Risks

- Finished audio is much harder than MIDI.
- Lyria 3 may return a finished audio clip rather than separated drum stems.
- Lyria 3 output format may need local conversion before the package can expose `.wav` files.
- Generating master first and separating stems is harder than generating stems first and mixing a master.
- Sample licensing and provenance matter.

### Success Criteria

- A drum-loop package can be generated with a master and stems.
- All stems match the master length.
- The package can be dragged into a DAW.
- Metadata records BPM, bars, style, stem paths, Lyria model ID, prompt, and source audio format.

## Phase 4: Dataset Mode For Chords And Drums

### Objective

Prepare the project for future learning or retrieval by importing chord MIDI event data and registering drum-loop audio/stem metadata.

### Deliverables

- Chord MIDI event extraction.
- Drum-loop metadata ingestion.
- Stem package metadata ingestion.
- Dataset example schemas.
- Provenance and licensing fields.
- Dataset summaries.

### Required Architecture Changes

- Add dataset schemas independent of generation.
- Separate generated outputs from reference/training data.
- Add source metadata and licensing fields early.

### Suggested Modules/Files

- `vibedrop_ai/datasets/chord_midi.py`
- `vibedrop_ai/datasets/drum_audio.py`
- `vibedrop_ai/datasets/schemas.py`
- `vibedrop_ai/scripts/import_dataset.py`
- `tests/test_chord_dataset_import.py`
- `tests/test_drum_dataset_metadata.py`

### Success Criteria

- Project-generated chord MIDI can be parsed back into event data.
- Drum-loop stem packages can be registered with metadata.
- Dataset entries are inspectable and validated.

## Phase 5: Retrieval Or Small ML Model

### Objective

Use the dataset layer to support retrieval or small ML models for chord MIDI event plans and drum-loop assets.

### Deliverables

- Chord event tokenization or embedding.
- Drum-loop metadata/features.
- Retrieval baseline.
- Optional small model after enough data exists.
- Evaluation metrics.

### Success Criteria

- Retrieval or model output produces valid chord event plans or drum-loop plans.
- Outputs pass the same validators as AI planner output.
- The ML layer remains optional.

## What Should Not Be Built Yet

Do not build yet:

- Melody generation.
- Raw MIDI binary generation by an LLM.
- Full song generation.
- Non-drum Lyria 3 generation.
- Real-time plugin features.
- Complex audio mastering.
- Custom audio ML before drum data exists.
- Large ML dependency stacks.

## Portfolio Value

This roadmap demonstrates practical AI engineering:

- AI authors structured musical events.
- The app validates unsafe AI output.
- The app writes reliable MIDI files.
- Drum output becomes a usable producer asset package.
- Dataset work prepares for retrieval and ML without premature model training.

The key portfolio story is that Vibe Drop AI turns creative AI output into reliable DAW-ready assets through validation, packaging, and deterministic export.

## Recommended Near-Term Sequence

1. Remove melody from supported plans and validation.
2. Define `ChordMidiPlan` and `ChordNoteEvent`.
3. Create a hand-written chord event JSON file.
4. Validate and render that event plan to MIDI.
5. Add AI prompt-to-event-plan generation.
6. Add chord quality validation and repair.
7. Define the drum-loop package format.
8. Add Lyria 3 drum-loop master generation through Gemini API `generateContent`.
9. Add drum-loop stem packaging or separation later.

# Projector Spec

**Purpose** Build a reproducible snapshot of canon, belief, and tone context for any scene and emit a context pack for downstream generation tooling.

## Inputs

- `records/**/record.json` with accompanying `.meta.json` for provenance
- `canon/characters/**/timeline.json` (per-character event streams)
- `scene_index/**.json` for tone tags and scene functions
- `tag_registry.json`

## Core States

- **Truth state:** Canon facts valid at scene S. Past events are immutable; corrections require an explicit `correction` event with provenance.
- **Belief state (per character):** Facts each character believes at scene S. Use `belief: true|false` flags on timeline events and propagate downstream.
- **Inventory/skill state (per character):** Active skills, titles, classes, and items with rank/grade. Enforce monotonic rules.
- **Tone context:** Sliding window (size K) of recent `tone_tag[]` and `scene_function[]` values to bias style.

## Precedence and Merge Rules

1. Timeline observations at or before S override static `record.json` data if conflicts arise.
2. When characters disagree, prefer the observation with higher provenance certainty. If identical certainty, surface the conflict and mark `truth_conflict: true`.

## Outputs

- `context_pack.json`

  ```json
  {
    "scene_id": "01.02.01",
    "world_state": { "summary": "canon facts at this cutoff" },
    "character_state": {
      "arnold": { "beliefs": [], "inventory": [] },
      "jake": { "beliefs": [], "inventory": [] }
    },
    "recent_tone": {
      "tone_tag": ["recursive_logic"],
      "scene_function": ["tutorial_prompt"]
    },
    "mechanic_rules": ["Distilled mechanic statements with citations"],
    "citations": [{ "scene_id": "01.02.01", "line_start": 10, "line_end": 12 }],
    "constraints": {
      "forbid_new_ids": true,
      "allowed_tag_categories": ["narrative_style", "scene_function", "system_mechanic"]
    }
  }
  ```
- Optional `diff_report.md` summarising changes between S−1 and S.

## Algorithm (v1)

- Topologically sort timeline events up to scene S.
- Reduce skill/item/class states with monotonic checks:
  - Grade cannot decrease unless a `downgrade_event` is present.
  - Skill levels are non-decreasing unless explicitly reset.
- Build tone context from the previous K scenes (default K = 3).
- Extract mechanic rule spans by scanning for `system_mechanic` tags and pull high-certainty quotes into the context pack.

## Validation

- Fail if any generated state requires inline provenance instead of sidecar citations.
- Fail if tags in the context pack are not `status: approved`.
- Warn when the tone context window is empty.

# Export Bundle Spec

**Purpose** Provide JSONL bundles that mix stylistic, mechanical, and narrative exemplars for RAG or SFT.

## Format

- Each JSONL line must validate against `schemas/export_bundle.schema.json`.
- Spans are deduplicated by `(scene_id, line_start, line_end, anchor_hash)`.

## Inclusion Rules

- Only include spans whose tags resolve to `status: approved` in the registry.
- Compute weights per span:
  - `certainty`: map `high → 1.0`, `medium → 0.6`, `low → 0.2`.
  - `tone`: 1.0 if a span carries `narrative_style` or `character_tone`; otherwise 0.5.
  - `mechanics`: 1.0 if `system_mechanic` is present; otherwise 0.2.

## Bundles

- `bundle_style.jsonl` for tone and stylistic exemplars.
- `bundle_mechanics.jsonl` for mechanic rules with quotes.
- `bundle_story.jsonl` for multi-line narrative windows.

## Usage

- **RAG:** retrieve K entries per bundle, for example `{ K_style: 8, K_mechanics: 6, K_story: 8 }`.
- **SFT (optional):** filter to `certainty ≥ 0.6`, cap examples to ≤1000 tokens, and include citations as inline footnotes.

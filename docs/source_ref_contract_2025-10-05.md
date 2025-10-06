# 🔍 PHI `source_ref[]` Contract

Updated: 2025-10-05

## Purpose

The `source_ref[]` field tracks where a fact, event, or tag is grounded in the text.

## Structure

```json
{
  "type": "scene", // or wiki | user | inferred | external
  "scene_id": "01-02-01",
  "line_start": 120,
  "line_end": 132,
  "quote": "Jake vanished mid-dash..."
}
```

## Rules

- `scene_id` must follow: `BB-CC-SS` format
- `line_start <= line_end`
- `quote` is optional but preferred (max ~280 chars)
- `type` is required (default: `scene`)

## Where Used

- In timeline events (`timeline.json`)
- In `.meta.json` for per-ID provenance
- Not inline in canon `records/`, except where explicitly allowed

## Why It Matters

- Gives every claim a traceable proof
- Enables LLM audit, retraction, or quote-sourcing
- Distinguishes inferred vs. seen data
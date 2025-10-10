# 📄 `contracts/source_ref_contract_v1.1.md` (v1.1)

**Status:** Final (subcontract)
**Updated:** 2025‑10‑07
**Owned by:** PHI Data Contracts

## Purpose

Defines the **canonical structure and validation rules** for `source_ref[]` entries used across PHI to justify facts,
tags, and events.

This doc is **atomic** and referenced by:

- `provenance_contract.md` (placement & philosophy)
- Schemas for `.meta.json`, `timeline.json`, and `tag_registry.meta.json`

## Scope

- Structure of a single `source_ref` object
- Allowed `type` values
- Validation rules (format, ranges, required fields)
- Examples and anti‑patterns

## Object Definition

```json
{
  "type": "scene",            // enum: scene | wiki | user | inferred | external
  "scene_id": "BB.CC.SS",     // book-chapter-scene (e.g., "01.02.01"), required for type=scene
  "line_start": 120,          // 1-based inclusive
  "line_end": 132,            // 1-based inclusive, must be >= line_start
  "quote": "Jake vanished mid-dash...",  // optional; recommended; length-limited
  "certainty": "high",        // optional: low | medium | high
  "inference_type": "character_assumption", // optional; requires inference_note if present
  "inference_note": "Jake thinks it's a dream; narrator suggests otherwise."
}
```

### Field Notes

- `type`:

  - `scene`: primary; references a scene span
  - `wiki`: out‑of‑universe encyclopedia page (rare)
  - `user`: editor/annotator assertion (must be low certainty unless co‑cited)
  - `inferred`: computed from multiple refs; **must** include `inference_note`
  - `external`: author comment, Patreon Q&A, etc. (must include how to locate it)
- `scene_id`: strict `BB.CC.SS` (zero‑padded)
- `quote`: truncate to stay token‑friendly; the span is authoritative, the quote is convenience

## Validation Rules (Schema)

- `type` **required**; default to `"scene"` only if omitted by legacy data migration
- If `type = "scene"`:

  - `scene_id` **required** and must match `^\d{2}\.\d{2}\.\d{2}$`
  - `line_start` & `line_end` **required**, integers ≥ 1, and `line_start <= line_end`
- `quote` optional but **preferred**; **max length: 320 characters**
(Rationale: keeps context chunks compact; 320 is a sweet spot between 280 and 400. If you want 400 later, we can bump,
but set one number to end bikeshedding.)
- If `inference_type` present → `inference_note` **required**
- If `certainty = "low"` → record must be explicitly **reviewed** before downstream use
- No HTML or Markdown except minimal italics/quotes; normalize smart quotes; strip spoilers
- type: "inferred" is permitted only when the consuming schema or registry field (allow_inferred: true) explicitly allows it.

## Placement Rules (summary; see provenance contract for full)

- Never store `source_ref[]` inside **canon** `record.json`
- Allowed locations:

  - `.meta.json` sidecars (for global facts)
  - `timeline.json` events (for observed state)
  - `tag_registry.meta.json` (to justify approved tags)

## Examples

### A. Straight scene citation

```json
{
  "type": "scene",
  "scene_id": "01.02.01",
  "line_start": 118,
  "line_end": 126,
  "quote": "System Message: Skill gained — Meditation."
}
```

### B. Inferred behavior with note

```json
{
  "type": "scene",
  "scene_id": "01.05.02",
  "line_start": 170,
  "line_end": 182,
  "quote": "As he slept, the wound closed slowly. The System chimed...",
  "certainty": "high",
  "inference_type": "system_behavior_guess",
  "inference_note": "Health regen inferred from healing speed + System message."
}
```

### C. External comment

```json
{
  "type": "external",
  "quote": "Author Q&A on Patreon (2024-07-12): Meditation does not stack with Potion Regen.",
  "certainty": "medium",
  "inference_note": "Out-of-universe; use with caution; prefer in-text confirmation."
}
```

## Anti‑Patterns (Do Not Do)

- ❌ Embedding `source_ref[]` inside `record.json`
- ❌ `line_start > line_end`
- ❌ `scene_id` like "BB-CC-SS" (hyphenated) or "1.2.3" (missing zero-padding)
- ❌ `inference_type` without `inference_note`
- ❌ Using `user` type for anything that should be `inferred` (be honest)

## JSON Schema (fragment)

*(Drop into `schemas/shared/source_ref.schema.json`)*

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://primal-hunter.local/schemas/shared/source_ref.schema.json",
  "title": "source_ref",
  "$comment": "See docs/contracts/source_ref_contract_v1.1.md#object-definition",
  "type": "object",
  "description": "Canonical citation object proving a fact, event, or tag.",
  "required": [
    "type"
  ],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "scene",
        "wiki",
        "user",
        "inferred",
        "external"
      ],
      "description": "Where this citation originates."
    },
    "scene_id": {
      "type": "string",
      "pattern": "^\\d{2}\\.\\d{2}\\.\\d{2}$",
      "description": "Scene identifier in dotted BB.CC.SS format (Book, Chapter, Scene)."
    },
    "line_start": {
      "type": "integer",
      "minimum": 1,
      "description": "First line number (inclusive) backing this reference."
    },
    "line_end": {
      "type": "integer",
      "minimum": 1,
      "description": "Last line number (inclusive) backing this reference."
    },
    "quote": {
      "type": "string",
      "maxLength": 320,
      "description": "Optional quote excerpt to provide immediate context."
    },
    "certainty": {
      "type": "string",
      "enum": [
        "low",
        "medium",
        "high"
      ],
      "description": "Confidence rating for inferred or external citations."
    },
    "inference_type": {
      "type": "string",
      "enum": [
        "character_assumption",
        "system_behavior_guess",
        "narrative_foreshadow",
        "other"
      ],
      "description": "Why this reference is inferred rather than explicit."
    },
    "inference_note": {
      "type": "string",
      "minLength": 3,
      "description": "Supporting explanation for inferred references."
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "type": {
            "const": "scene"
          }
        },
        "required": [
          "type"
        ]
      },
      "then": {
        "required": [
          "scene_id",
          "line_start",
          "line_end"
        ]
      }
    },
    {
      "if": {
        "properties": {
          "type": {
            "const": "inferred"
          }
        },
        "required": [
          "type"
        ]
      },
      "then": {
        "required": [
          "inference_note"
        ]
      }
    },
    {
      "if": {
        "required": [
          "inference_type"
        ]
      },
      "then": {
        "required": [
          "inference_note"
        ]
      }
    }
  ],
  "additionalProperties": false
}
```

> Note: JSON Schema’s `$data` for cross‑field checks may require Ajv or similar; if your validator can’t do it, implement `line_start <= line_end` in Python.

## Relationship to Provenance Contract

- This doc defines **the shape** of a `source_ref`
- `provenance_contract.md` defines **where** refs live and **how** they’re used (timeline precedence, review gates, etc.)
- If the two conflict, **provenance contract wins on placement**, and this doc wins on **object validity**

---

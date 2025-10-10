# 📜 PHI Provenance & Canon Data Contract (v2.0)

**Status:** Final  
**Updated:** 2025-10-07  
**Supersedes:** all prior provenance drafts (2025-10-05 / 10-06)  
**Maintainer:** PHI Design Lead (user)

---

## Purpose

This contract defines how **canonical facts, events, and tags** in the Primal Hunter Index (PHI) are tracked, justified,
and aligned using provenance metadata.

It supports:

- 🔗 Canon alignment via `source_ref[]`
- 🧠 Narrative scaffolding via `tone_tag[]` and `scene_function[]`
- 🧾 Change history via `record_log[]`
- 🎯 Controlled inference through structured metadata

---

## 0) Design Goals

- **Referential solidity**: facts, events, tags, reviews, and quotes all point at stable IDs.
- **Small canon, rich context**: the payload you RAG over is clean; deep metadata stays out of band.
- **Append-only history**: you can layer new knowledge without rewriting the past.
- **Toolable**: validators, CLIs, and editors can follow one consistent contract.

---

## 1. Canon Data Philosophy

### ✅ Canon is quote-backed

#### Storage separation (hard rule)
Canonical payloads in `records/**` MUST NOT contain `source_ref[]`. Provenance MUST be recorded **only** in:
- `timeline.json` events (subjective, per-event citations), or
- sidecar metadata files (e.g., `.meta.json`, `.provenance.json`) for objective facts.

This keeps canon lean and immutable while provenance captures the evidence and context that justify it.

- Facts in records/ are canonical only if they are supported by provenance recorded in **timelines or sidecars** (not inline in the canon payload)
- The old `canon: true` boolean is **soft-deprecated** — provenance proves canon

### ✅ Canon is not fixed — it evolves

- New scenes can add or revise understanding of a fact
- **Timelines**, not static files, are the source of truth for progression or observed parameters

---

## 2. Provenance Requirements

| File Type                         | Provenance Required? | Notes |
|----------------------------------|-----------------------|-------|
| `records/**/*.json`              | ✅ Yes                | Via `.meta.json` sidecar with `source_ref[]` |
| `tag_registry.json`              | ✅ Yes                | Canon tags must be quote-backed unless marked `allow_inferred: true` |
| `tag_candidates.json`            | ❌ No                 | Heuristic only |
| `scene_index/**/*.json`          | ❌ No                 | Taggable for tone but not canonical |
| `timeline.json`                  | ✅ Yes (per event)    | Events must have `source_ref[]` |
| `.meta.json`                     | ✅ Yes                | Tracks source and review status |
| `.review.json`                   | ⚠️ Optional           | Adds human/Codex QA notes |

“See docs/runbooks/provenance_workflow.md for a detailed list of datasets that require provenance.” |
---

## 3. `source_ref[]` — The Provenance Spine

### 📐 Structure

```json
{
  "type": "scene",               // or: wiki, user, inferred, external
  "scene_id": "01.02.01",
  "line_start": 111,
  "line_end": 120,
  "quote": "Jake vanished mid-dash...",
  "certainty": "high",           // optional: low | medium | high
  "inference_type": "character_assumption",   // optional enum
  "inference_note": "Jake thinks it’s a dream, but we know it’s real."
}
````

### 🎯 Rules

- `type` is required
  - `scene_id`, `line_start`, `line_end` are required for `type: scene`
- `quote` is optional but recommended (≤ 320 characters)
- If `inference_type` is set, `inference_note` is required
- If `certainty` is `"low"`, review must confirm entry

- Canon payloads (record.json) must not include source_ref[]. All provenance lives in:
  - timeline.json (for event-based facts)
  - .meta.json sidecar (for global facts)
  - tag_registry.meta.json (for tag definitions)

Timeline events take precedence over record.json content when computing state at a given point in time. Canon records
describe general properties. Timeline events log observed state and take priority when in conflict.

### ✅ Valid Inference Types

| Type                    | Meaning                                                         |
| ----------------------- | --------------------------------------------------------------- |
| `character_assumption`  | The character states or implies a thing, but it may not be true |
| `system_behavior_guess` | We infer system logic from its output                           |
| `narrative_foreshadow`  | A later fact is teased but not yet revealed                     |
| `other`                 | Use `inference_note` to clarify                                 |

---

## 4. `record_log[]` — Tracking Change History

Lives in `.meta.json`. Required for every canonical ID.

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-06" },
  { "action": "approved", "by": "user", "date": "2025-10-07" },
  { "action": "edited", "by": "user", "field": "description", "from": "Old", "to": "New", "date": "2025-10-09" }
]
```

Enables:

- Safe diffing
- Historical audits
- Human or Codex review trails

---

## 5. Tone Tagging and Narrative Weight

Timeline events and scene index entries may include:

```json
"tone_tag": ["deadpan_humor", "recursive_logic"],
"scene_function": ["tutorial_prompt", "power_scaling_moment"]
```

These are NOT canon facts — they are narrative metadata to help:

- RAG pipelines weight tone/stylistic alignment
- QA workflows track genre drift
- Codex-generated stories stay in character voice

### 💡 All tags used must

- Appear in `tag_registry.json`
- Be marked `"status": "approved"` or fail validation
- Have `source_ref[]` in `.meta.json` unless `allow_inferred: true`

---

## 6. Where Provenance Lives

| Location                 | What it proves                            |
| ------------------------ | ----------------------------------------- |
| `.meta.json`             | Canon fact justification                  |
| `timeline.json`          | Event-based observations or state changes |
| `.review.json`           | QA justification or override              |
| `.provenance.json`       | (Optional) Scene-to-ID inverse lookup     |
| `tag_registry.meta.json` | Justifies use of tags in canon files      |

---

## 7. What Not to Do

🚫 Don’t put `source_ref[]` inline in `records/**.json` 🚫 Don’t use tags without approving them + providing provenance 🚫
Don’t assert “canon” without a quote, even if “it’s obvious” 🚫 Don’t override past facts — add new events with new
provenance

---

## 8. Provenance as Alignment System

Provenance is not just a citation tool — it’s the foundation of *tone-faithful, canon-consistent generation*.

- It lets us trace what’s quote vs inference
- It allows weighting by certainty
- It enables backtracking of hallucinations
- It trains Codex to write faithfully to style rules without breaking them

---

## 9. Enforcement & Tooling

Validation tooling must:

- Enforce `source_ref.type`
- Require quote-backed references for `allow_inferred: false`
- Require `record_log[]` in `.meta.json`
- Fail if timeline events lack `source_ref[]`
- Flag if `certainty` is low but no `inference_note` is given
- Validate that every `source_ref.scene_id` matches an existing file in `scene_index/**`
- Validate that `line_start` and `line_end` fall within that scene’s defined bounds
- All sidecar files (.meta.json, `.review.json`, `.provenance.json`) must validate against their respective schemas
  before promotion or RAG export.

### 🔧 Provenance Validator Expectations

The official validator (`tools/validate_provenance.py`) enforces the following:

1. **Timeline coverage** — Every event must include a non-empty `source_ref[]` array with valid `scene_id`, `line_start`,
   and `line_end`.  
2. **Inline provenance ban** — `source_ref` keys are disallowed in canonical payloads outside timelines or `.meta.json`
   sidecars.  
3. **Record log validation** — If present, `record_log[]` must be an array of objects with `date` and `action`.  
4. **Soft guidance** — Warn (not fail) if an event contains neither a `quote` nor an `inference` hint.  
5. **Scene ID regex** — Enforce `^\d{2}\.\d{2}\.\d{2}$` for all `scene_id` strings.  

Violations:

- ❌ Hard fails (exit 1) on structural or inline-source_ref errors.  
- ⚠️ Warnings for missing quotes or inference flags.

---

## 10. Related Contracts

| File                                               | Purpose                                     |
| -------------------------------------------------- | ------------------------------------------- |
| [`record_log_contract_v1.1.md`](record_log_contract_v1.1.md) | Format + rationale for `record_log[]`       |
| [`source_ref_contract_v1.1.md`](source_ref_contract_v1.1.md) | Legacy source_ref structure                 |
| [`tagging_contract_v0.4.md`](tagging_contract_v0.4.md)       | Tag structure, approval status, usage rules |
| [`tone_contract.md`](../runbooks/tone_contract.md)           | Writing constraints and tone logic          |

---

## 11. Glossary

- **Canon** — Quote-backed, structurally validated fact
- **Provenance** — Scene/quote span that justifies a fact or tag
- **Inference** — A claim that extrapolates from a quote (must be declared)
- **Timeline** — Per-character event log of when canon facts were observed
- **Sidecar** — Any contextual metadata file linked to a canon record:
              - `.meta.json` — source refs, record log, who added/edited it
              - `.review.json` — QA, approvals, warnings, Codex notes
              - `.provenance.json` — optional reverse scene-to-ID lookup

---

## 12. Review Philosophy (Optional)

Codex-generated facts may be marked as `"proposed"` until reviewed. Reviewers may:

- Approve or reject entire records
- Override inferred values with stricter quotes
- Flag low-certainty sources
- Add warnings to `review.json`

Only `"approved"` records are eligible for downstream RAG or fine-tuning.

---

### Related Docs

- [Source Ref Contract](./source_ref_contract_v1.1.md)
- [Record Log Contract](./record_log_contract_v1.1.md)
- [Provenance Workflow Runbook](../runbooks/provenance_workflow_runbook.md)
- [tools/validate_provenance.py](../../tools/validate_provenance.py)

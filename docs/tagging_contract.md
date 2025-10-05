# 🏷 Tagging Contract (PHI) — v0.2

## Why this exists
We use tags in two very different ways — one for automation, one for canon. This contract documents the structure, rules, and intended behavior of tagging within the PHI project.

---

## Core Principles

- **Design first.** Tagging schemas and registries are defined before data is added.
- **Registry-driven.** All tags used in canon must be listed in `tag_registry.json`, with metadata.
- **Two layers, same shape.** Heuristic tags and canonical tags use the same structure, but have different trust levels.
- **One file, not two.** Tag roles are tracked via metadata (`status`, `allow_inferred`)
- **No blobs.** Every tag exists to support search, training, or filtering — no vague extras.

---

## Tag Lifecycle

| Field            | Purpose                                                     |
|------------------|-------------------------------------------------------------|
| `tag`            | Snake_case ID (e.g., `basic_archery`)                       |
| `status`         | `"candidate"` (scraped), `"approved"` (usable), `"rejected"`|
| `allow_inferred` | `true` = tag can be guessed by LLM/tagger                   |
| `aliases`        | Optional list of synonyms (not used in canon)              |
| `notes`          | Optional editorial metadata                                 |

---

## Tag Layers

### 1) Heuristic Tagging (pre‑ingest assist)
- **Goal:** speed up ingest (pre-sort, suggestions, context).
- **Source:** scraped vocab + alias matching + simple heuristics + (optionally) LLM hints.
- **Reliability:** may be wrong; must be reviewed before being used as canon.

### 2) Canonical Tagging (post‑ingest metadata)
- **Goal:** maximize useful retrieval (RAG filters, analytics, timelines).
- **Source:** quote-backed scenes/events; must pass schema + registry checks.
- **Reliability:** strict; only **approved** registry tags allowed.

## Tag Usage

- All tags used in `scene_index/`, `timeline.json`, etc. must exist in `tag_registry.json` and be `status: "approved"`.
- Tags may be **inferred by tools** only if `allow_inferred: true`.
- Canon tags must be backed by quotes or strong context. Heuristic tags are for ingest only.

---

## File Roles

| File                            | Role                              |
|----------------------------------|-----------------------------------|
| `tagging/tag_candidates.json`   | Scraped, unreviewed raw tags      |
| `tagging/tag_registry.json`     | Source of truth for valid tags    |


---

## Schema Contracts

- `tags.schema.json` – used inline in scene/timeline records (just string arrays).
- `tag_registry.schema.json` – used to validate the structure and metadata of all approved tags.

---

## Promotion Flow

```text
[Scraped] --> tag_candidates.json
    |
[Reviewer promotes selected tags]
    v
tag_registry.json (status: "approved")
    |
[Tags now usable in scene_index.json]
```

---

## Example

### Registry
```json
{
  "skills": [
    {
      "tag": "meditation",
      "status": "approved",
      "allow_inferred": false,
      "aliases": ["meditating"]
    }
  ],
  "scene_type": [
    {
      "tag": "social_scene",
      "status": "approved",
      "allow_inferred": true
    }
  ]
}
```

### Scene
```json
"tags": {
  "skills": ["meditation"],
  "scene_type": ["social_scene"]
}
```

---

## Open Design Questions

- Do we want to support `confidence` or `inferred_from` per scene tag?
- Should tags be namespaced (`skill:meditation`) later?
- Do tags ever need per-record `source_ref[]`?

---

_Last updated: 2025-10-07_

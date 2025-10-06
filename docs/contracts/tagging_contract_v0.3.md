# 🏷️ Tagging Contract (PHI) — v0.3

**Status:** Final (v0.3)

**Updated:** 2025‑10‑06

**Supersedes:** Tagging Contract v0.2 (2025‑10‑05) (see changelog)

---

## Why this exists

We use tags in two distinct ways: (1) **heuristic pre‑ingest** to accelerate human review and data entry, and (2) **canonical post‑ingest** to power search/RAG and analytics. This contract pins the vocabulary, lifecycle, IDs, and file roles so schemas and tools can be implemented consistently.

---

## Changelog

* **v0.3 (2025‑10‑06)**

  * Split **lifecycle** (`status`) from **purpose** (`tag_role`).
  * Clarified **promotion** semantics: candidates → registry entries with `status: "candidate"`, not auto‑approved.
  * Required **stable IDs** for tags (`tag_id`), aligned with the PHI Stable ID Contract.
  * Defined exact **file shapes** for `tag_candidates.json`, `tag_registry.json`, and inline `tags` usage.
  * Added `source`, `notes`, optional review fields (`reviewed_by`, `reviewed_at`).
* **v0.2 (2025‑10‑05)**

  * Single‑layer registry with `status` and `allow_inferred`; heuristic vs canonical implied.

---

## Core Principles

* **Design first:** docs → schemas → code.
* **Registry‑driven:** all tags used in canon must exist in `tag_registry.json` and be `status: "approved"`.
* **Heuristic ≠ Canon:** same object shape, different trust level + `tag_role`.
* **Everything referencable has a stable ID:** tags included.
* **Sidecars carry process, canon carries facts.**

---

## Vocabulary & Fields

### Identity

* `tag_id` (string, required): Stable ID per **ID Contract**. Format: `tag.<namespace>.<slug>` (lowercase snake_case). Examples: `tag.skills.basic_archery`, `tag.scene_type.romantic_scene`.
* `tag` (string, required): The local slug used inline in scenes/timelines (e.g., `basic_archery`, `romantic_scene`).

### Classification

* `type` (string, required): Domain bucket (e.g., `skill`, `scene_type`, `entity`, `location`, `race`, `god`, `class`, etc.).
* `tag_role` (string, required): Purpose of the tag.

  * Allowed: `heuristic` | `canonical` | `test_data` | `inferred_only` | `manual_only`
  * Guidance:

    * `heuristic`: for pre‑ingest sorting and LLM suggestion; not guaranteed true.
    * `canonical`: approved, reliable, used in RAG/analytics.
    * `test_data`: scaffolding for pipelines; never promoted for canon use.
    * `inferred_only`: tag never appears literally; allowed inference if context warrants.
    * `manual_only`: too subtle for automation; only human may apply.

### Lifecycle

* `status` (string, required): Lifecycle state.

  * Allowed: `candidate` | `approved` | `rejected`
  * Semantics:

    * `candidate`: unverified; usable for heuristic tagging **only**.
    * `approved`: verified; allowed in canon; used for RAG/analytics.
    * `rejected`: previously considered; do not use unless re‑opened with rationale.
* `approved` (boolean, required): Redundant safety flag; **must** be `true` iff `status == "approved"`.

### Policy & Metadata

* `allow_inferred` (boolean, default `false`): If `true`, tools may apply tag without explicit keyword match (contextual inference allowed).
* `aliases` (string[], optional): Synonyms to help match heuristics; not used in canon payloads.
* `description` (string, required): Human‑readable label/summary.
* `source` (string, optional): Origin (e.g., `wiki_scrape`, `manual_entry`, `consolidated_from:tag_x`).
* `notes` (string, optional): Editorial notes.
* `reviewed_by` / `reviewed_at` (optional): Audit for approval/rejection.

---

## File Roles & Shapes

### 1) `tagging/tag_candidates.json` (loose input)

* Purpose: scraped vocab + manually added candidates for consideration.
* Shape (per namespace): compact, can be **strings or objects**.

```jsonc
{
  "skills": [
    "Basic Archery",
    { "tag": "meditation", "aliases": ["meditating"], "notes": "seeded manually" }
  ],
  "scene_type": ["romantic_scene", "social_scene"],
  "entity": ["jake", "arnold", "minaga"]
}
```

### 2) `tagging/tag_registry.json` (source of truth)

* Purpose: structured, validated tag objects across namespaces.
* Shape: **object of arrays** by namespace; each entry fully specified.

```jsonc
{
  "skills": [
    {
      "tag_id": "tag.skills.basic_archery",
      "tag": "basic_archery",
      "type": "skill",
      "tag_role": "canonical",
      "status": "approved",
      "approved": true,
      "allow_inferred": false,
      "aliases": ["archery_basic"],
      "description": "Basic proficiency with bows and crossbows.",
      "source": "manual_entry",
      "reviewed_by": "jess",
      "reviewed_at": "2025-10-06"
    },
    {
      "tag_id": "tag.skills.hunters_sight",
      "tag": "hunters_sight",
      "type": "skill",
      "tag_role": "heuristic",
      "status": "candidate",
      "approved": false,
      "allow_inferred": true,
      "aliases": ["hunter's sight", "huntersight"],
      "description": "Candidate: skill reference scraped from wiki.",
      "source": "wiki_scrape"
    }
  ],
  "scene_type": [
    {
      "tag_id": "tag.scene_type.romantic_scene",
      "tag": "romantic_scene",
      "type": "scene_type",
      "tag_role": "canonical",
      "status": "approved",
      "approved": true,
      "allow_inferred": true,
      "description": "A scene where romance is a central intent."
    }
  ]
}
```

### 3) Inline usage in records (scenes/timelines)

* Canon files may only use **approved** tags.
* Inline shape (validated by `tags.schema.json`):

```json
"tags": {
  "skills": ["basic_archery"],
  "scene_type": ["romantic_scene"]
}
```

**Rule:** if a tag appears inline, it MUST exist in `tag_registry.json` with `status: "approved"` and `approved: true`.

---

## Promotion & Approval Flow

```text
[Scraped] → tag_candidates.json (strings/objects)
    │
    ├─ promote_tags (enrichment)
    │    • infer namespace → `type`
    │    • generate `tag_id` (tag.<ns>.<slug>)
    │    • normalize to object
    │    • set `tag_role: heuristic`, `status: candidate`, `approved: false`
    │    • merge into tag_registry.json (atomic)
    │
    └─ reviewer approval (human or CLI)
         • flip `status: approved`, `approved: true`
         • optionally set `tag_role: canonical`
         • add `reviewed_by`, `reviewed_at`
```

**Never** auto‑approve on promote.

---

## Guardrails & Validation

* All `tag_id` values must follow the **Stable ID Contract** (`tag.<ns>.<slug>`).
* `status == "approved"` ⇒ `approved == true` (and vice‑versa).
* Inline tags in scenes/timelines must resolve to registry entries with `status: "approved"`.
* Heuristic use of tags (LLM or regex) requires either literal match OR `allow_inferred: true`.
* `tag_role` must be present and conform to allowed set.

---

## Open Design Notes

* We may add `confidence` or `inferred_from` per *scene* tag in the future (not in registry).
* Consider `namespaces` beyond the initial set (e.g., `injury`, `event_tag`).

---

## Implementation Checklist (post‑doc)

1. Update `tag_registry.schema.json` to match v0.3 fields and rules.
2. Update `tag_candidates.schema.json` to allow strings **or** partial objects per namespace.
3. Implement `tools/promote_tags.py` enrichment pipeline per this doc.
4. Enforce inline approval in `tags.schema.json` or via validator.
5. Add Makefile targets for promote/approve flows.

---

## References

* Stable IDs: see **PHI Stable ID Contract** (`tag.` prefix reserved).
* Provenance architecture: timelines keep `source_ref[]`; registry is fact catalog.


---


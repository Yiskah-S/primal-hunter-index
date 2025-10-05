# 🏷 Tagging Contract (PHI) — v0.1

## Why this exists
We have two different tagging layers (heuristic vs canonical) and a shared tag registry. This doc is the single source of truth for **what tags are**, **where they live**, **how they’re validated**, and **why** we do it this way.

---

## Core Principles
- **Contract before data.** Schema-first: define shapes, then populate.
- **One registry to rule them all.** All tags used anywhere must exist in the registry (with status).
- **Two layers, one shape.** Heuristic tags and canonical tags share the same format; their **validation bar** differs.
- **Records are canon only.** `records/` contain quote-backed truth. Non-canon vocab (candidates, registry) lives outside `records/`.

---

## Tag Layers

### 1) Heuristic Tagging (pre‑ingest assist)
- **Goal:** speed up ingest (pre-sort, suggestions, context).
- **Source:** scraped vocab + alias matching + simple heuristics + (optionally) LLM hints.
- **Reliability:** may be wrong; must be reviewed before being used as canon.
- **Where:** temporary outputs / proposals (not in `records/`).

### 2) Canonical Tagging (post‑ingest metadata)
- **Goal:** maximize useful retrieval (RAG filters, analytics, timelines).
- **Source:** quote-backed scenes/events; must pass schema + registry checks.
- **Reliability:** strict; only **approved** registry tags allowed.
- **Where:** inline in `scene_index/` and `timeline.json` (canon files).

---

## Data Artifacts

- `tagging/tag_candidates.json`  
  Raw scraped buckets by category. **Unreviewed**. May contain junk.  
  _Used by reviewers/tools to promote into the registry._

- `tagging/tag_registry.json`  
  Approved tag vocab (with metadata). **Source of truth** for allowed tags.  
  _Only tags with `"status": "approved"` can be used in canon._

- `scene_index/**.json`  
  Scene files with a `tags` block referencing **approved** registry tags.

- `records/**`  
  Canon data only (quote‑backed). Tags here must be registry‑approved.

---

## Schemas & $refs

- `schemas/tags.schema.json`  
  Defines the **shape of a tags block** (array of snake_case strings).  
  **$ref this** anywhere tags appear (scene files, events, items).

- `schemas/tag_registry.schema.json`  
  Defines the **shape of the registry** (categories, entries, metadata like `aliases`, `status`, `notes`).

- (Optional later) `schemas/tag_candidates.schema.json`  
  Light validation for scraped candidate structure (not required to start).

**Rule:** scene/timeline schemas should `$ref` `tags.schema.json`.  
**Validation:** tooling must ensure scene tags ∈ registry where `status == "approved"`.

---

## Naming & Formatting

- **snake_case**, ASCII only; no spaces.  
  e.g., `archers_eye`, `malefic_viper`, `basic_archery`, `social_scene`.

- Avoid over-namespacing early. If needed later, consider `domain:tag` (e.g., `skill:meditation`) once we have a good reason.

- **Aliases** live in the registry (for matching heuristics), never in canon files.

---

## Promotion Workflow (Candidates → Registry → Canon)

1. **Scrape:** `tools/extract_tag_targets.py` → `tagging/tag_candidates.json`.
2. **Review/Promote:** approve useful entries into `tagging/tag_registry.json` with:
   - `status: "approved"` (vs `"candidate"`/`"rejected"`)
   - optional `aliases`, `notes`.
3. **Apply:** use **approved** tags in scene/timeline `tags` blocks (validated by schema + registry).

---

## Validation Rules

- **Heuristic outputs** may contain non-approved tags → **cannot** go into `records/`.
- **Canon files (scene/timeline)**:
  - `tags` **must** be strings validated by `tags.schema.json`.
  - each tag **must** exist in `tag_registry.json` with `status: "approved"`.
- Optional soft rules:
  - Warn if tag appears w/o helpful context (`inference`/`confidence`) when not quote-backed.
  - Warn on inline `source_ref[]` in places other than timeline or designated sidecars.

---

## Tooling (Current & Planned)

- ✅ `tools/extract_tag_targets.py`  
  API-based scraper: categories → pages (names only).

- ⏭ `tools/promote_tags.py` (planned)  
  Assist reviewers in moving candidates → approved registry, with diffs.

- ⏭ `tools/tagger.py` (planned)  
  Heuristic matcher + optional LLM hints → proposal files (not canon).

- ⏭ `tools/validate_provenance.py` (planned)  
  Guardrails for source_ref in timeline; soft‑deprecate `canon: true`.

---

## Open Questions (intentionally parked)
- Do we add `confidence` / `inferred_from` to tags used in scenes?
- Should we support namespacing (`skill:meditation`) in registry now or later?
- Do we need a `tag_groups` concept (e.g., `scene_type` as mutually exclusive)?

---

## Appendix: Quick Examples

### Tag block inside a scene (canon)
```json
"tags": {
  "skills": ["meditation", "basic_archery"],
  "gods": ["malefic_viper"],
  "characters": ["jake", "caleb"],
  "scene_type": ["social_scene"]
}

# 🧠 Tagging & Provenance Pipeline – PHI Project Overview

This document captures the finalized strategy for heuristic tagging, sidecar structure, and provenance management prior to the Golden Slice.

---

## ✅ Provenance Architecture (Finalized)

| Layer              | Role |
|--------------------|------|
| `timeline.json`    | Truth-source of observed state (e.g., skill learned, stat gained) |
| `.meta.json`       | File-level audit (created by, updated by, record_log[]) |
| `source_ref[]`     | Only inside timeline events or .meta sidecars |
| `canon: true`      | Optional/legacy only — not required or enforced |

**Rules:**

- No inline `source_ref[]` in records like `skills.json` or `equipment.json`
- Detailed provenance lives in the timeline, or in `.meta.json` as needed
- `.meta.json` = minimal metadata, not detailed scene mapping
- All per-entry `source_ref[]` should go into timeline events or future `.provenance.json` files

---

## 🗂 Planned Sidecar Types

| Sidecar              | Role |
|----------------------|------|
| `.meta.json`         | Who created the file, when, current `record_log[]`, review status |
| `.review.json`       | Tracks reviewer decisions, Codex results, human QA notes |
| `.provenance.json`   | (Optional) Maps which scenes contribute to which data entries |

---

## 🏷 Heuristic Tagging Pipeline (Pre–Golden Slice)

### Goal:
Tag early chapters with characters, gods, skills, locations, etc., using a hybrid pipeline.

### 🔄 Pipeline Flow:

| Stage              | Role |
|--------------------|------|
| 📥 Scraper         | Extract vocab from PH Wiki (skills, gods, races, etc.) |
| 🧠 Tag registry    | Populate `tag_registry.json` from scraped + curated terms |
| ⚙️ Heuristic tagger| Match vocab in chapter text |
| 🤖 LLM pass        | Classify context: POV mention, ability used, historical, etc. |
| 👩‍💻 Human review  | Final approve/edit |
| ✅ Save tags       | Output `tags` per scene file, validated via `tags.schema.json` |

### Tag Output Format (per scene):
```json
"tags": {
  "characters": ["Jake", "Caleb"],
  "gods": ["Malefic Viper"],
  "skills": ["Meditation", "Basic Archery"],
  "locations": ["Starter Zone"]
}
```

---

## 📌 Order of Operations

1. Build `extract_tag_targets.py` → scrape PH wiki categories (skills, races, gods...)
2. Generate + validate `tag_registry.json`
3. Write `tagger.py` (or `apply_tags.py`) to match chapters → tags
4. Review tag results + LLM-enhance if needed
5. THEN build `scene_index/` + `timeline.json` for Golden Slice with tags in place

---

## ❌ What Not To Do

- Don’t store `source_ref[]` inline in skills.json, equipment.json, etc.
- Don’t rely on `canon: true` to mean anything without provenance
- Don’t write the Golden Slice until tagging and vocab are prepped

---

_Last updated: 2025-10-06_
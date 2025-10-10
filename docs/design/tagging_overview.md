# 🧠 Tagging Pipeline

Status: Informational

This document captures the finalized strategy for heuristic tagging, sidecar structure, and provenance management prior
to the Golden Slice.

See [`tagging_contract.md`](./tagging_contract.md) for all tagging design rules.

---

## ✅ Provenance Architecture (Finalized)

| Layer              | Role |
|--------------------|------|
| `timeline.json`    | Truth-source of observed state (e.g., skill learned, stat gained) |
| `.meta.json`       | File-level audit (created by, updated by, record_log[]) |
| `source_ref[]`     | Only inside timeline events or .meta sidecars |
| `canon: true`      | Optional/legacy only — not required or enforced |

**Rules:**

- No inline `source_ref[]` in canonical payloads like `records/skills/sn.*/record.json` or `records/equipment/*.json`
- Detailed provenance lives in the timeline, or in `.meta.json` as needed
- `.meta.json` = minimal metadata, not detailed scene mapping
- All per-entry `source_ref[]` should go into timeline events or future `.provenance.json` files

---

## 🏷 Heuristic Tagging Pipeline (Pre–Golden Slice)

### Goal

Tag early chapters with characters, gods, skills, locations, etc., using a hybrid pipeline.

### 🔄 Pipeline Flow

| Stage              | Role |
|--------------------|------|
| 📥 Scraper         | Extract vocab from PH Wiki (skills, gods, races, etc.) |
| 🧠 Tag registry    | Populate `tag_registry.json` from scraped + curated terms |
| ⚙️ Heuristic tagger| Match vocab in chapter text |
| 🤖 LLM pass        | Classify context: POV mention, ability used, historical, etc. |
| 👩‍💻 Human review  | Final approve/edit |
| ✅ Save tags       | Output `tags` per scene file, validated via `tags.schema.json` |

---

## 📌 Order of Operations

1. Build `extract_tag_targets.py` → scrape PH wiki categories (skills, races, gods...)
2. Generate + validate `tag_registry.json`
3. Write `tagger.py` (or `apply_tags.py`) to match chapters → tags
4. Review tag results + LLM-enhance if needed
5. THEN build `scene_index/` + `timeline.json` for Golden Slice with tags in place

---

## ❌ What Not To Do

- Don’t store `source_ref[]` inline in per-entity payloads (`records/skills/sn.*/record.json`, equipment records, etc.)
- Don’t rely on `canon: true` to mean anything without provenance
- Don’t write the Golden Slice until tagging and vocab are prepped

---

**Last updated:** 2025-10-07

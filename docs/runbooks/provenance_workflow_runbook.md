# 🧪 Provenance Workflow (Runbook)

**Status:** Living  
**Updated:** 2025-10-07  
**Audience:** Human contributors and Codex prompting  
**Maintainer:** PHI Data Engineering

---

## Purpose

This runbook documents how to fill out `source_ref[]` blocks in `.meta.json` and `timeline.json` accurately, using
tooling support and step-by-step heuristics.

---

## 1. Use the Golden Skill Spotlight Pattern

Before bulk-tagging skills, pick **one skill** and:

- Populate its `record.json` canon fields
- Fill out `.meta.json` with:
  - `record_log[]`
  - `source_ref[]`
  - `index_meta` (`added_by`, `reviewed_by`, etc.)
- Add at least one timeline event that reflects when the character gained or used this skill
- Validate the record and preview in a browser/editor

If any field is unquoteable, the schema or tagging pipeline might need to change. This record becomes the **reference
template** for future automation.

---

## 2. Use `search_skill_mentions.py` to Generate Candidate Snippets

Use this CLI tool to search across all `scene_index/**` files for mentions of a term (e.g., `"Meditation"`), then:

- Output a manifest of scene IDs and matching line numbers
- Manually review results
- Fill `source_ref.scene_id`, `line_start`, `line_end` based on selected quote chunks

Use the best representative quote (≤ 320 characters) for `source_ref.quote`.

---

## 3. Use Editor Previews to Help Target Quotes

When entering `source_ref` manually, the `json_editor` app:

- Auto-loads `scene_id` previews
- Displays scene metadata (title, characters, line range)
- Lets you highlight/select a line range from the viewer directly

This minimizes line number errors and ensures that all `source_ref`s point to visible, human-reviewed text.

---

## 4. Edge Case Tips

- If multiple quotes justify a fact, use a `source_ref[]` array
- If a fact is inferred, set `inference_type` + `inference_note` and flag for review
- If a tag is canonical but the text doesn’t literally match, `allow_inferred: true` must be set in `tag_registry.json`

---

## 5. Before You Approve

Make sure that:

- Every `source_ref.scene_id` points to a real scene in `scene_index/**`
- `line_start` and `line_end` are inside that scene’s bounds
- Any `certainty: "low"` entry has been reviewed and confirmed
- All approved tags used in `tags` blocks have corresponding sidecar provenance

---

## 6. Where Provenance Is Required

| Dataset                                 | Rationale                                     |
|-----------------------------------------|-----------------------------------------------|
| `records/skills/`                       | Per-node mechanics, upgrades, lore            |
| `records/equipment.json`                | Item descriptions, origins                    |
| `records/titles.json`                   | Acquisition method, effects                   |
| `records/classes.json`                  | Class reveals, bonuses                        |
| `records/affinities.json`               | Affinity usage, lore                          |
| `records/races.json`                    | Species traits, tiers                         |
| `records/locations.json`                | Descriptions, first appearances               |
| `records/zone_lore.json`                | Regional revelations                          |
| `records/system_glossary.json`          | Term introductions                            |
| `records/global_event_timeline.json`    | Major events and outcomes                     |
| `records/global_announcement_log.json`  | System messages and context                   |
| `records/tiers.json`                    | Tier system explanations                      |
| `records/stat_scaling.json`             | Stat interactions or tests                    |
| `records/affiliations.json`             | Faction introductions, philosophies           |
| `records/creatures.json`                | Creature sightings, behavior                  |

💡 Tip: If the record appears in records/, assume it needs provenance unless marked as test_data or scaffold.

Any new canon dataset should follow the same pattern.

## 7) Sample Workflows

- Add a skill → `sf.*` + `sn.*` + `.meta.json` + `timeline.json` (optional)
- Update a skill → add `timeline` entry + amend `.meta.json`
- Upgrade path → create new `sn.*` and link via `.meta.json`
- Promote a tag → update `tag_registry.json` + tag’s `.meta.json`

---

### Optional: Tag Justification Blocks

Reviewers may include human-readable justifications per tag for LLM transparency:

```json
"tags_justification": {
  "spectral": "teleport effect described as phasing out",
  "ambush": "attacked from behind"
}
These may live in timeline.json events or .review.json sidecars.
They are non-canonical, for audit and training notes only.


📍 Add as **non-canon optional field** (audit only).  
We can schema-ize it later under `review.schema.json`.

---

## 8) Extended Workflow Recipes

### 🧩 8.1 Add a New Skill (Minimal Flow)

1. **Create the Family:**  
   - If `sf.*` doesn’t exist, create it under `records/skills/`.  
1. **Add the Node:**  
   - Create a new `sn.*` entry in `records/**` with minimal canon fields (`id`, `family_id`, `description`, `tags`).  
1. **Attach Metadata:**  
   - Create `.meta.json` beside it containing `index_meta`, `record_log[]`, and at least one `source_ref[]`.  
1. **If Discovered In-Scene:**  
   - Add a timeline event referencing `node_id` with the same `source_ref`.  
1. **Validate:**  
   - Run `validate_all_metadata.py` before committing.

---

### 🔁 8.2 Enrich an Existing Skill After a New Chapter

1. Append a new timeline event with updated or new `observed_params`.  
1. Include a supporting `source_ref[]` quote for the new observation.  
1. If the information stabilizes across multiple scenes or explicit System confirmation:  
   - Update the skill node’s `record.json` fields.  
   - Log the change in `record_log[]` with `action: "edited"`.  
1. **Review:**  
   - If the change alters interpretation, add a reviewer note in `.review.json`.  
1. **Re-validate.**

💡 **Stability Threshold:**  
When a fact has been seen multiple times or explicitly stated by the System, it becomes “canon-level stable” and should migrate from `timeline` to `record.json`.

---

### ⛓️ 8.3 Create an Upgrade Path

1. Add a new skill node (`sn.<skill>.rankX`).  
1. In the prior node’s `.meta.json`, append:  
   ```json
   { "type": "upgrades_to", "target": "sn.<skill>.rankX" }
   ```

1. Optionally, in the new node, add the reverse link:

   ```json
   { "type": "upgrades_from", "target": "sn.<skill>.rankN" }
   ```

1. Re-run `validate_all_metadata.py` to ensure both IDs resolve.
1. Update the relevant character’s `timeline.json` to record the rank-up event.

---

### 🏷️ 8.4 Promote a Tag Candidate

1. Run `tools/promote_tags.py`.

   - Choose the tag and namespace (`skills`, `scene_type`, etc.).
   - Set the `status` to `"candidate"`.
1. Decide whether it may be inferred (`allow_inferred: true | false`).
1. Write the new tag to `tag_registry.json` with a `.meta.json` entry containing:

   - `index_meta` (who/when/method)
   - `record_log[]` (added + approved)
   - `source_ref[]` quote if `allow_inferred: false`
1. During validation, any scene using a not-yet-approved tag should fail.
1. Once reviewed, run `approve_tags.py` to flip `status: "approved"` and regenerate sidecar.

---

## Tools Mentioned

| Tool | Role |
|------|------|
| `search_skill_mentions.py` | Find scenes mentioning an entity; output scene IDs + line spans |
| `json_editor` | UI for editing `.meta.json`, picking scene spans |
| `validate_all_metadata.py` | Runs full-schema + provenance enforcement |
| `promote_tags.py` | Promotes candidates to registry entries |
| `approve_tags.py` | Flips status, generates sidecars |

---

## See Also

- [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)
- [`contracts/record_log_contract.md`](../contracts/record_log_contract.md)
- [`contracts/source_ref_contract.md`](../contracts/source_ref_contract.md)

---

---

### Related Docs

- [Provenance Contract](../contracts/provenance_contract_v2.0.md)
- [Source Ref Contract](../contracts/source_ref_contract_v1.1.md)
- [Record Log Contract](../contracts/record_log_contract_v1.1.md)
- [tools/validate_provenance.py](../tools/validate_provenance.py)

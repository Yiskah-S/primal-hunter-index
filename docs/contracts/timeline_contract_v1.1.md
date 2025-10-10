# Timeline Contract (PHI) — v1.1 (Final)

**Status:** Final (v1.1)
**Updated:** 2025‑10‑10
**Supersedes:** Timeline Contract v1.0 (adds `knowledge_delta`, defines event types, adopts dotted scene IDs, clarifies ordering) 

**Linked Schemas**

* `schemas/timeline_event.schema.json` (this object)
* `schemas/shared/source_ref.schema.json` (citations; update to dotted pattern per this contract) 
* `schemas/shared/id.schema.json` (ID regex & namespaces) 
* `schemas/shared/tags.schema.json` (inline tag usage; registry-backed) 

**Context**
Timelines are the **epistemic spine** that let PHI reconstruct “who knew what, when,” using scene‑anchored receipts and strict IDs. They sit between clean canon facts (`records/**`) and the projector that replays state at a scene.  

---

## 1) Purpose & Scope

This contract defines the canonical structure of **per‑character timelines** (`records/characters/<character_slug>/timeline.json`) and the validation rules for each **event** they contain.
Timelines **do not** mutate canon records; they **explain** when knowledge changed and **prove it** with `source_ref[]`. Provenance placement rules are inherited from the Provenance Contract (timelines/sidecars only). 

---

## 2) Storage & File Shape

* **Path:** `records/characters/<character_slug>/timeline.json`
* **Shape:** **ordered array** of event objects (see §3).
* **Canonical scene ID format:** `BB.CC.SS` (dotted, zero‑padded; e.g., `01.02.01`). This replaces the old hyphenated form. Tools/validators must enforce the dotted regex. (Source‑Ref schema will be updated accordingly.) 

---

## 3) Event Object — Fields

| Field                   | Type     | Req? | Notes                                                                                                 |
| ----------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------- |
| `event_id`              | string   | ✅    | Format: `ev.<char_slug>.<BB>.<CC>.<SS>.<slug>`; must satisfy ID regex.                                |
| `scene_id`              | string   | ✅    | Dotted `BB.CC.SS`. Anchors `source_ref` spans and file order.                                         |
| `order`                 | integer  | ✅    | 1‑based order within the scene.                                                                       |
| `type`                  | string   | ✅    | Controlled enum (see §4).                                                                             |
| `source_ref`            | array    | ✅    | Per‑event receipts; **only** place where inline provenance is allowed in timelines.                   |
| `tags`                  | string[] | ⛔    | Must resolve to **approved** registry entries if present.                                             |
| `notes`                 | string   | ⛔    | Free text for human readers; ignored by tools.                                                        |
| `knowledge_delta`       | object[] | ⛔    | Required for knowledge‐changing types; see §5.                                                        |
| `node_id`               | string   | ⛔    | `sn.*` when the event pertains to a specific skill node.                                              |
| `from_node_id`          | string   | ⛔    | For `skill_evolved`/`skill_upgraded`.                                                                 |
| `to_node_id`            | string   | ⛔    | For `skill_evolved`/`skill_upgraded`.                                                                 |
| `corrects_event_id`     | string   | ⛔    | For `belief_corrected`.                                                                               |
| `from_id`               | string   | ⛔    | For `information_received` (speaker/source: `pc.*`, `npc.*`, `sys.*`).                                |
| `topic_id`              | string   | ⛔    | Topic entity (`sf.*`, `sn.*`, `cl.*`, `eq.*`, `loc.*`, …).                                            |
| `epistemic_at.scene_id` | string   | ⛔    | Dotted `BB.CC.SS`. If present, defines *when the character actually knew it*. Defaults to `scene_id`. |
| `diegetic_hint`         | object   | ⛔    | Optional world‑chronology breadcrumbs (`realm`, `era`, `sequence`); advisory only.                    |

**IDs only.** All cross‑references must use stable IDs (`sn.*`, `sf.*`, `pc.*`, …), never names. 

---

## 4) Event Types (Closed Set)

Extending this set requires a predicate/enum update (do not invent verbs ad hoc).

### 4.1 Knowledge Events

- `skill_acquired` — character gains a node.
  - **Fields:** `node_id` (`sn.*`) required.
  - **Delta:** required (capturing newly known rarity/effect parameters).

- `skill_observation` — new or clarified parameters of a node.
  - **Fields:** `node_id` required.
  - **Delta:** required; captures additional knowledge about the existing node.

- `skill_evolved` — **within-rank enhancement** (no System-recognised rank/tier change).
  - **Fields:** `node_id` required.
  - **Delta:** required; describes improved potency/cost/cooldown within the same node.
  - **Forbidden:** `from_node_id`, `to_node_id`.

- `skill_upgraded` — **rank/tier upgrade** recognised by the System (new node).
  - **Fields:** `from_node_id` and `to_node_id` (`sn.*` → `sn.*`) required.
  - **Delta:** optional but recommended (e.g., rarity shift).
  - **Forbidden:** `node_id`.

- `information_received` — hearsay/instruction (`from_id` required; `topic_id` optional; `knowledge_delta` optional).
- `belief_corrected` — correct a prior belief (`corrects_event_id` + `knowledge_delta` required).
- `memory_lost` — delete/obscure prior belief (optional `knowledge_delta` to mark fields unknown).

### 4.2 System / World / Social

* `system_message_broadcast`, `class_changed`, `title_granted`, `quest_completed`
* `conversation`, `training_session`, `deal_made`, `combat_action`, `location_discovered`

**Rule:** Knowledge‑changing types require `knowledge_delta` (see §5).

---

## 5) `knowledge_delta` — Grammar

A delta states *what just became known or changed*.

```json
{
  "field_path": "effects.mana_cost",   // dot path relative to the referenced ID's schema
  "new_value": 20,                     // the newly known value
  "old_value": "unknown",              // optional, for corrections
  "confidence": 1.0,                   // 0.0–1.0; separate from source_ref.certainty
  "scope": "character_view"            // enum: character_view | narrator_hint | system_tooltip
}
```

**Rules**

* Include **only** changed/revealed paths; do not restate entire objects.
* `confidence` here expresses *belief strength*; `source_ref[].certainty` expresses *citation strength*. 
* Deltas **do not** mutate node files; the projector uses them to compute state at a scene.  

---

## 6) Ordering & Time Axes

Three clocks, two views:

- **File order (reader view):** keep the JSON sorted by `scene_id` (book order), then `order` to keep diffs tidy and citations adjacent. 
- **Epistemic order (projector view):** reconstruct character knowledge by sorting on `epistemic_at.scene_id` when present, otherwise `scene_id`, then `order`. 
- **Diegetic time:** optional breadcrumbs only; surface via `diegetic_hint` when the story demands it. 
- **Provenance anchor:** `source_ref[]` always cites the book-order span associated with `scene_id`. 

---

## 7) Provenance (Authoritative)

* Every event **must** include at least one valid `source_ref` span (`scene_id`, `line_start`, `line_end`). 
* Timelines are the canonical home for event‑level citations; canonical payloads elsewhere **must not** embed `source_ref[]` (use sidecars). 
* Quotes in events should be short (≤ 320 chars recommended by Source‑Ref Contract). 

---

## 8) Referential Integrity & Immutability

* Use **IDs everywhere**; never names. 
* Multi‑character scenes are logged **separately** in each character’s timeline; `scene_id` provides linkage. 
* Timelines are **append‑only**. To correct a mistake, add a `belief_corrected` event that references `corrects_event_id`; do not edit history. 
* Skill/system data must **not** be embedded inline; reference `sn.*`/`sf.*` IDs and express changes via `knowledge_delta`. 

---

## 9) Validation Rules (Tool‑Enforced)

Validators must assert:

1. `event_id` matches `^ev\.[a-z0-9_]+\.([0-9]{2}\.){2}[0-9]{2}\.[a-z0-9_]+$` and `scene_id` matches `^\d{2}\.\d{2}\.\d{2}$`. 
2. `source_ref[]` non‑empty; each entry valid per Source‑Ref Contract (structure, ranges, certainty/inference notes if used). 
3. If `type ∈ {skill_acquired, skill_observation, skill_evolved, belief_corrected}`, then `knowledge_delta` is **required**.
   - For `skill_evolved`: `node_id` **required**; `from_node_id`/`to_node_id` **forbidden**.
   - For `skill_upgraded`: `from_node_id` and `to_node_id` **required**; `node_id` **forbidden**; `knowledge_delta` optional but recommended.
4. All referenced IDs (`sn.*`, `sf.*`, `pc.*`, etc.) exist in canon. 
5. `tags[]` (if present) resolve to **approved** registry entries. 
6. `additionalProperties: false` — unknown fields rejected.
7. Timelines **do not** contain `record_log[]` (lives in `.meta.json` sidecars). 

---

## 10) Examples

**A. Skill acquired (book‑order reveal = epistemic moment)**

```json
{
  "event_id": "ev.jake.01.02.01.skill_acquired_meditation",
  "scene_id": "01.02.01",
  "order": 1,
  "type": "skill_acquired",
  "node_id": "sn.meditation.rank1",
  "knowledge_delta": [
    { "field_path": "rarity", "new_value": "Inferior", "confidence": 1.0 },
    { "field_path": "effects.passive", "new_value": "Minor clarity boost", "confidence": 0.9 }
  ],
  "source_ref": [
    { "type": "scene", "scene_id": "01.02.01", "line_start": 120, "line_end": 130, "quote": "System: Skill gained — Meditation." }
  ],
  "tags": ["system_message", "epistemic_gain"],
  "notes": "Tutorial award."
}
```

**B. Within-rank evolution (overlay delta)**

```json
{
  "event_id": "ev.jake.03.04.02.skill_evolved_meditation_synergy",
  "scene_id": "03.04.02",
  "order": 4,
  "type": "skill_evolved",
  "node_id": "sn.meditation.rank1",
  "knowledge_delta": [
    { "field_path": "effects.hp_recovery", "new_value": "minor_increase", "confidence": 0.9 }
  ],
  "source_ref": [
    { "type": "scene", "scene_id": "03.04.02", "line_start": 88, "line_end": 95 }
  ],
  "notes": "Improved technique unlocked within rank1; no System rank change."
}
```

**C. Rank/tier upgrade (new node lineage hop)**

```json
{
  "event_id": "ev.jake.01.05.01.skill_upgraded_meditation_rank2",
  "scene_id": "01.05.01",
  "order": 2,
  "type": "skill_upgraded",
  "from_node_id": "sn.meditation.rank1",
  "to_node_id": "sn.meditation.rank2",
  "knowledge_delta": [
    { "field_path": "rarity", "new_value": "Common", "old_value": "Inferior", "confidence": 1.0 }
  ],
  "source_ref": [
    { "type": "scene", "scene_id": "01.05.01", "line_start": 44, "line_end": 60 }
  ],
  "notes": "System rank-up: new node created; lineage recorded in skills."
}
```

---

## 11) Anti‑Patterns

* ❌ Embedding skill stats in the event instead of using `node_id`. 
* ❌ Deleting or mutating past events; append a `belief_corrected` instead. 
* ❌ Using names for cross‑refs; IDs only. 
* ❌ Omitting `source_ref[]` (even for “obvious” scenes). 
* ❌ Applying unapproved tags. 

---

## 12) Relationship to Other Contracts

* **Provenance Contract:** placement of citations (timelines & sidecars), timeline precedence for progression. 
* **Source-Ref Contract:** citation object structure; **this contract updates the canonical `scene_id` format to dotted** and expects schema/tools to follow. 
* **ID Contract:** stable ID regex; `ev.*` composition and cross-ref requirements. 
* **Tagging Contract:** inline tag usage must resolve to approved registry entries. 
* **Skills Contract:** timelines reference `sn.*`/`sf.*` by ID; node evolution is recorded via events (and lineage in records), not in-place edits. 
* **Conceptual Ontology Contract:** defines global relationship predicates (e.g., `is_instance_of`, `upgrades_from`, `belongs_to_system`) that type the graph. Timelines reference nodes by ID; higher-order meaning (edges/predicates) lives in the ontology. 

---

## 13) JSON Schema Fragment (reference)

> Embed in `schemas/timeline_event.schema.json` and import the shared `source_ref` schema. Adjust `$id` to your repo domain.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://phi/schemas/timeline_event.schema.json",
  "title": "Timeline Event",
  "type": "object",
  "additionalProperties": false,
  "required": ["event_id", "scene_id", "order", "type", "source_ref"],
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^ev\\.[a-z0-9_]+\\.[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}\\.[a-z0-9_]+$"
    },
    "scene_id": { "type": "string", "pattern": "^\\d{2}\\.\\d{2}\\.\\d{2}$" },
    "order": { "type": "integer", "minimum": 1 },
    "type": {
      "type": "string",
      "enum": [
        "skill_acquired", "skill_observation", "skill_evolved", "skill_upgraded",
        "information_received", "belief_corrected", "memory_lost",
        "system_message_broadcast", "class_changed", "title_granted", "quest_completed",
        "conversation", "training_session", "deal_made", "combat_action", "location_discovered"
      ]
    },
    "node_id": { "type": "string", "pattern": "^sn\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$" },
    "from_node_id": { "type": "string", "pattern": "^sn\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$" },
    "to_node_id": { "type": "string", "pattern": "^sn\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$" },
    "from_id": { "type": "string", "pattern": "^(pc|npc|sys)\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$" },
    "topic_id": { "type": "string", "pattern": "^(sf|sn|eq|cl|rc|loc)\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$" },
    "corrects_event_id": { "type": "string", "pattern": "^ev\\.[a-z0-9_]+\\.[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}\\.[a-z0-9_]+$" },
    "knowledge_delta": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["field_path", "new_value"],
        "additionalProperties": false,
        "properties": {
          "field_path": { "type": "string", "minLength": 1 },
          "new_value": {},
          "old_value": {},
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "scope": { "type": "string", "enum": ["character_view", "narrator_hint", "system_tooltip"] }
        }
      }
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9_]+$" },
      "uniqueItems": true
    },
    "notes": { "type": "string" },
    "source_ref": {
      "type": "array",
      "$ref": "https://phi/schemas/source_ref.schema.json"
    },
    "epistemic_at": {
      "type": "object",
      "additionalProperties": false,
      "required": ["scene_id"],
      "properties": {
        "scene_id": { "type": "string", "pattern": "^\\d{2}\\.\\d{2}\\.\\d{2}$" }
      }
    },
    "diegetic_hint": {
      "type": "object",
      "additionalProperties": true
    }
  },
  "allOf": [
    { "if": { "properties": { "type": { "const": "skill_acquired" } } }, "then": { "required": ["node_id", "knowledge_delta"] } },
    { "if": { "properties": { "type": { "const": "skill_observation" } } }, "then": { "required": ["node_id", "knowledge_delta"] } },
    {
      "if": { "properties": { "type": { "const": "skill_evolved" } } },
      "then": {
        "required": ["node_id", "knowledge_delta"],
        "not": { "anyOf": [ { "required": ["from_node_id"] }, { "required": ["to_node_id"] } ] }
      }
    },
    {
      "if": { "properties": { "type": { "const": "skill_upgraded" } } },
      "then": {
        "required": ["from_node_id", "to_node_id"],
        "not": { "required": ["node_id"] }
      }
    },
    { "if": { "properties": { "type": { "const": "belief_corrected" } } }, "then": { "required": ["corrects_event_id", "knowledge_delta"] } }
  ]
}
```

---

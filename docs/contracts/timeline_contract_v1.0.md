Title: Timeline Contract (PHI)  
Status: Final (v1.0)  
Updated: 2025-10-08  
Supersedes: none (new file)  
Linked Schemas:  
  - schemas/character_timeline.schema.json  
  - schemas/shared/source_ref.schema.json  
  - schemas/shared/id.schema.json  
  - schemas/shared/tags.schema.json  
  - schemas/shared/provenance.schema.json  

---

## 1. Purpose and Scope

This contract defines the canonical structure and validation rules for **character timelines** within the Primal Hunter Index (PHI).  
Timelines are the **epistemic spine** of the project — recording not only what occurs, but also what each entity *knows* at each point in time.

Timelines bridge the gap between:
- **Objective canon** (facts in `records/`)  
- **Subjective knowledge** (character beliefs, discoveries, misunderstandings)

They provide the narrative context that allows the system to reconstruct character state at any scene in the story.

---

## 2. Structure Overview

Each file in `records/characters/<name>/timeline.json` is an **ordered array** of event objects.  
Events represent narrative actions, discoveries, or changes in knowledge, indexed to `scene_id` and line range.

```json
[
  {
    "event_id": "ev.jake.01-02-01.acquire_skill_meditation",
    "scene_id": "01-02-01",
    "order": 1,
    "type": "skill_acquired",
    "skill_id": "sn.meditation.inferior",
    "source_ref": [
      {
        "type": "scene",
        "scene_id": "01-02-01",
        "line_start": 110,
        "line_end": 125
      }
    ],
    "notes": "System tutorial reward after first meditation attempt.",
    "tags": ["system_message", "epistemic_gain"]
  }
]
````

---

## 3. Required Fields

| Field          | Type    | Description                                     |
| -------------- | ------- | ----------------------------------------------- |
| `event_id`     | string  | Stable, unique ID (`ev.<char>.<scene>.<slug>`). |
| `scene_id`     | string  | Canonical scene reference in `BB-CC-SS` format. |
| `order`        | integer | Event order within the scene (1-based).         |
| `type`         | string  | Controlled enum of event categories (see §4).   |
| `source_ref[]` | array   | Provenance citations per Source Ref Contract.   |
| `tags[]`       | array   | Semantic tags (must exist in tag registry).     |
| `notes`        | string  | Optional prose context for human readers.       |

---

## 4. Event Categories

Grouped by epistemic function:

### 4.1 Knowledge Events

Events that alter what the character *knows*.

* `insight_gained` — new understanding or realization
* `belief_corrected` — false assumption corrected
* `memory_lost` — loss of information or amnesia
* `information_received` — hearsay, dialogue, or instruction

### 4.2 System Events

Changes in in-world System state.

* `skill_acquired`
* `skill_upgraded`
* `class_changed`
* `title_granted`
* `quest_completed`

### 4.3 World Events

Physical or environmental actions.

* `combat_action`
* `item_crafted`
* `location_discovered`
* `system_message_broadcast`

### 4.4 Social Events

Interactions and relationships.

* `conversation`
* `training_session`
* `deal_made`
* `bond_formed`

Each category maps to controlled validation rules and permissible cross-links.

---

## 5. Referential Rules

1. **ID Linkage**

   * Cross-reference other records only by ID (`sn.*`, `sf.*`, `eq.*`, `cl.*`, etc.).
   * Never embed skill or item data inline.

2. **Order Semantics**

   * Sort chronologically by `scene_id`, then numerically by `order`.
   * Scene order defines absolute timeline position.

3. **Immutability**

   * Timeline entries are *immutable historical records*.
   * To correct an event, append a new one with `type: correction` referencing the original `event_id`.

4. **Cross-Referencing**

   * Use `related_to[]` for narrative or causal linkage (“this follows from that”).
   * Always reference by `event_id`.

5. **No Global Events**

   * Multi-character scenes are logged separately in each relevant character’s file.
   * Shared `scene_id` provides linkage across perspectives.

---

## 6. Provenance and Validation

1. **Every event must include at least one valid `source_ref`.**

   * Required fields: `type`, `scene_id`, `line_start`, `line_end`.
   * Inferred or ambiguous entries must set `certainty` and `inference_note`.

2. **All referenced IDs must exist in canon.**

   * Validator cross-checks all foreign keys (skills, equipment, classes, etc.).

3. **Tags must resolve to the tag registry.**

   * Unregistered tags trigger soft warnings in validator.

4. **Inline provenance forbidden** except inside the `source_ref[]` block.

   * All other provenance belongs in `.meta.json` or in the event-level citations.

5. **Strict schema enforcement:**

   * `additionalProperties: false` required.
   * Unknown fields are rejected at validation time.

---

## 7. Record Log Integration

Timeline files **do not include `record_log[]` internally** — they *are* the canonical chronological record.
The `.meta.json` sidecar logs editorial changes such as imports, merges, or deletions, but narrative events remain immutable.

Example `.meta.json`:

```json
{
  "records": true,
  "entered_by": "assistant",
  "reviewed_by_human": false,
  "last_updated": "2025-10-08",
  "record_log": [
    {
      "entry_keys": ["timeline.json"],
      "method": "manual_entry",
      "date": "2025-10-08",
      "review_status": "approved"
    }
  ]
}
```

---

## 8. Projector Integration

`projector.py` consumes character timelines to reconstruct state snapshots at any given point.
This process computes:

* **Skill state** — which `sn.*` nodes are currently known
* **Belief state** — what the character *thinks* is true, including outdated or false info
* **Tag context** — active situational modifiers (`injured`, `training`, `in_party`, etc.)

This enables epistemic queries such as:

> “What did Jake know about the System before Nevermore?”
> “Which characters understood Meditation as of Book 03?”
> “When did Arnold’s perception of Oras shift from curiosity to reverence?”

---

## 9. Validator Expectations

The `validate_timeline.py` and `validate_provenance.py` tools enforce:

| Rule                                                  | Tool                     | Enforcement |
| ----------------------------------------------------- | ------------------------ | ----------- |
| Every event has non-empty `source_ref[]`              | validate_provenance.py   | Hard fail   |
| All `source_ref.scene_id` match `^\d{2}-\d{2}-\d{2}$` | validate_provenance.py   | Hard fail   |
| Unknown fields trigger error                          | validate_all_metadata.py | Hard fail   |
| Missing cross-refs (`sn.*`, etc.)                     | validate_all_metadata.py | Hard fail   |
| Unapproved tags                                       | validate_tag_registry.py | Warning     |
| Inline provenance in canon files                      | validate_provenance.py   | Hard fail   |

---

## 10. Crosslinks to Other Contracts

| Related Contract        | Relationship                                             |
| ----------------------- | -------------------------------------------------------- |
| **ID Contract**         | Defines `event_id` and ensures unique identifiers.       |
| **Provenance Contract** | Governs `source_ref[]` behavior and guardrails.          |
| **Source Ref Contract** | Defines the citation object structure.                   |
| **Record Log Contract** | Covers editorial audit for `.meta.json` changes.         |
| **Tagging Contract**    | Enforces tag schema and registry lookup.                 |
| **Skills Contract**     | Links timeline events to skill acquisition and upgrades. |

---

## 11. Anti-Patterns

❌ Don’t embed skill or stat data inline.
❌ Don’t modify or delete historical events — append instead.
❌ Don’t record omniscient knowledge.
❌ Don’t merge multi-character sequences into a single file.
❌ Don’t omit provenance — even inferred events require context.

---

## 12. Example Timeline Segment

**File:** `records/characters/jake/timeline.json`

```json
[
  {
    "event_id": "ev.jake.01-01-01.arrival",
    "scene_id": "01-01-01",
    "order": 1,
    "type": "system_message_broadcast",
    "source_ref": [
      { "type": "scene", "scene_id": "01-01-01", "line_start": 10, "line_end": 20 }
    ],
    "notes": "Jake receives first global System broadcast.",
    "tags": ["system_message"]
  },
  {
    "event_id": "ev.jake.01-02-01.skill_acquired_meditation",
    "scene_id": "01-02-01",
    "order": 2,
    "type": "skill_acquired",
    "skill_id": "sn.meditation.inferior",
    "source_ref": [
      { "type": "scene", "scene_id": "01-02-01", "line_start": 120, "line_end": 130 }
    ],
    "notes": "Jake gains Meditation skill at Inferior rank."
  }
]
```

---

## 13. Future Extensions

* **Multi-actor events:** Cross-timeline synchronization for team fights or shared missions.
* **Nested temporal layers:** Handle distorted realms (Nevermore, time chambers, etc.).
* **Partial knowledge modeling:** “Character suspects X” vs “Character knows X.”
* **Belief graph export:** Generate per-character epistemic graphs for LLM training.

---

*Updated 2025-10-08 — Authoritative contract for all timeline data.*

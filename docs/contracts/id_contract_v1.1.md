# 🆔 `contracts/id_contract_v1.1.md` (v1.1)

**Status:** Final
**Updated:** 2025-10-07
**Maintainer:** PHI Data Contracts
**Supersedes:** `id_contract_2025-10-05.md` (to be archived)

---

## 📘 Purpose

This contract defines the **stable ID system** used across the Primal Hunter Index (PHI). Stable IDs are machine-
parseable, cross-referencable, immutable labels that uniquely identify all core entities in the canonical corpus.

They enable:

- 🔗 Canon-safe referencing across timelines, records, tags, and scenes
- 🧾 Precise validation and schema enforcement
- 🧠 LLM-friendly prompt structuring
- 🎮 Future replay of character state and narrative progression

---

## 📐 ID Format

```regex
^(sn|sf|eq|cl|rc|pc|loc|tag|ev)\.[a-z0-9_]+(\.[a-z0-9_]+)*$
```

| Rule      | Explanation                                       |
| --------- | ------------------------------------------------- |
| Prefix    | Must match known namespace (see below)            |
| Segments  | One or more, separated by `.`                     |
| Style     | All lowercase, `snake_case` only                  |
| Separator | Always `.` between segments (never `/`, `-`, `:`) |

---

## 🔖 Prefixes and Namespaces

| Prefix | Meaning            | Examples                          |
| ------ | ------------------ | --------------------------------- |
| `sn.`  | Skill node         | `sn.meditation.rank1`             |
| `sf.`  | Skill family       | `sf.meditation`                   |
| `eq.`  | Equipment          | `eq.cloak_of_phasing`             |
| `cl.`  | Class              | `cl.void_warden`                  |
| `rc.`  | Race               | `rc.dryad`                        |
| `pc.`  | Character (person) | `pc.jake`, `pc.arnold`            |
| `loc.` | Location           | `loc.haven_city`, `loc.void_gate` |
| `tag.` | Internal tag key   | `tag.skills.teleportation`        |
| `ev.`  | Timeline event     | `ev.jake.01.02.01.a`              |

> Style note: timeline event IDs express the scene triplet as three dotted numeric segments (`<BB>.<CC>.<SS>`).

---

## 🛠️ ID Placement

### Provenance note
ID records and other canonical payloads MUST NOT embed `source_ref[]`. Provenance for those records belongs in sidecars and timelines. All cross-references must use IDs, not names.

- Every `record.json` in `records/**` must have an `id` field matching this contract
- `id` must match the filename (without `.json`) or directory (if bundled)
- Sidecars (`.meta.json`, `.review.json`, `.provenance.json`) are keyed by `id`
- Timeline events (`timeline.json`) must reference skill/equipment/class IDs by `id`, not name
- Tag definitions in `tag_registry.json` must use canonical `tag.`-prefixed keys

---

## 🔐 Immutability & Linking

### ❗ IDs are **immutable** once created

If an ID is renamed:

- The old ID is **deprecated** but not deleted
- A `links[]` array is added to the new `.meta.json`:

```json
"links": [
  {
    "type": "replaces",
    "target": "sn.meditation.tutorial_version",
    "reason": "Unified naming across characters"
  }
]
```

IDs never “move” — they are replaced, forked, or aliased, but never overwritten.

---

## 💡 Why IDs Matter

This system is the backbone of:

- Canon traceability
- Timelines that replay across chapters
- RAG pipelines that don’t hallucinate names
- Snapshot diffs of state at time `T`
- LLMs that speak in stable symbols (`sn.meditation.rank1` > “Meditation”)

Stable IDs make the PHI index **machine-safe**, not just human-readable.

---

## 🔎 Validation Rules

Enforced by: `tools/validate_ids.py`

| Rule                                               | Description                                                                      |
| -------------------------------------------------- | -------------------------------------------------------------------------------- |
| All `records/` entries must have `id`              | Stored at root of every `record.json`                                            |
| ID must match filename                             | `records/skills/sn.meditation.rank1/record.json` → `"id": "sn.meditation.rank1"` |
| All `id` fields must match regex                   | See top of file                                                                  |
| All timeline/meta/tag cross-references must use ID | Never use `"name": "Meditation"`                                                 |
| No whitespace, hyphens, camelCase, or uppercase    | All segments must be `snake_case`, dot-separated                                 |
| No duplicate IDs in repo                           | Will fail validation if ID exists in multiple places                             |

---

## 🧪 Examples

### A. Skill node

```json
{
  "id": "sn.blink.rank2",
  "family_id": "sf.blink",
  "rarity": "rare",
  "type": "combat_utility"
}
```

---

### B. Timeline event

```json
{
  "event_id": "ev.jake.01.02.01.a",
  "when": "01.02.01",
  "type": "skill_acquired",
  "node_id": "sn.blink.rank2"
}
```

---

### C. Meta key sidecar

```json
{
  "sn.blink.rank2": {
    "index_meta": { "added_by": "assistant" },
    "record_log": [...]
  }
}
```

---

### D. Tag registry entry

```json
{
  "tag.skills.blink": {
    "status": "approved",
    "category": "skills",
    "aliases": ["teleport", "instant_move"]
  }
}
```

---

## ❌ Anti-Patterns

| Pattern                                           | Problem                                                                    |
| ------------------------------------------------- | -------------------------------------------------------------------------- |
| `"Meditation"` instead of `"sn.meditation.rank1"` | Cannot be linked or validated                                              |
| `"sn.meditationRank1"`                            | Not snake_case                                                             |
| `"meditation.rank1"`                              | Missing prefix                                                             |
| `"sn.meditation_rank1"`                           | Snake_case used in multiple segments; should be `.` between logical levels |
| Reusing `id` for renamed entry                    | Violates immutability                                                      |

---

## 💾 Storage Summary

| File Type                     | Where ID goes                                          |
| ----------------------------- | ------------------------------------------------------ |
| `record.json`                 | `"id"` field                                           |
| `.meta.json` / `.review.json` | Top-level key (e.g. `"sn.blink.rank2": {...}`)         |
| `timeline.json`               | Cross-ref fields like `node_id`, `item_id`, `title_id` |
| `tag_registry.json`           | Top-level keys like `tag.skills.blink`                 |

---

## 🔗 Relationships

| Contract                 | Role                                                      |
| ------------------------ | --------------------------------------------------------- |
| `provenance_contract.md` | Canon records must have `id`; provenance is tracked by ID |
| `record_log_contract_v1.1.md` | History is tracked per-ID in `.meta.json`                 |
| `source_ref_contract_v1.1.md` | Quotes justify the contents of the record for each ID     |
| `tagging_contract_v0.4.md`    | Tags are defined and approved using IDed keys             |

---

## 🧠 Design Philosophy

> “Human-readable, machine-stable.”

Stable IDs are:

- Compact enough for Codex to read
- Explicit enough for humans to trace
- Rigid enough to prevent corruption or ambiguity

This is not just a naming convention. This is your **referential integrity layer.**

---

## 🛠 Future Tools That Rely on This

| Tool                  | Role                                                      |
| --------------------- | --------------------------------------------------------- |
| `build_meta_index.py` | Maps every `id` to its path + review status               |
| `projector.py`        | Replays state over time using only ID trails              |
| `validate_ids.py`     | Enforces ID correctness across the repo                   |
| `merge_bundle.py`     | Bundles all files under a given `id` into one review view |
| `tag_usage_map.py`    | Shows where each tag ID is referenced in canon            |

---

---

### Related Docs

- [Skills Contract](./skills_contract_v1.0.md)
- [Provenance Contract](./provenance_contract_v2.0.md)
- [ID Usage Guidelines](../design/storage_layout_design.md)
- [tools/validate_all_metadata.py](../../tools/validate_all_metadata.py)


Exactly — `cf.*` and `ci.*` were just shorthand to illustrate the distinction between *concept* and *instance.*
In your actual repo, you still want the **ID to carry semantic weight**.
That’s not redundancy; it’s free context for both humans and the LLM.

Think of the prefix as a *linguistic affordance*, not just a namespace.
It helps the model infer meaning even before it reads the metadata.

---

### 🧱 Example: explicit, language-rich IDs

Instead of:

```
cf.teleportation
ci.sn.teleportation.rank1
```

Use:

```
sf.teleportation           # skill family
sn.teleportation.rank1     # skill node (concept instance)
it.nanoblade.blackpoint    # item template
eq.nanoblade.blackpoint_001  # item instance (equip)
lc.haven_city_center       # location
pc.jake                    # player character
ev.jake.01.02.01.a                # event or scene
```

That’s not just naming; it’s *semantic compression.*
When the model later embeds or retrieves from vector space, “sn.” already biases toward *skill node* context.
It recognizes that “sn.teleportation.rank1” behaves like other `sn.*` things, not like `it.*` or `pc.*`.

---

### 🧩 Why we keep explicit type tags even with predicate edges

| Reason                            | Description                                                                                                                        |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **1. Natural language inference** | Models reason via token similarity. Seeing “skill_node” or “sn.” in the ID gives it cues about domain.                             |
| **2. Human readability**          | You and Codex can grep, diff, and validate far faster with semantically meaningful prefixes.                                       |
| **3. Schema modularity**          | Each prefix ties to a schema fragment (`skill_node.schema.json`, `location.schema.json`, etc.).                                    |
| **4. Mixed retrieval**            | When a query references “teleportation,” the system can cluster results across families, nodes, items, etc., by matching prefixes. |

So yes — keep the strong naming conventions:

* they help the model semantically,
* they help humans pragmatically,
* and they reinforce your `id_contract_v1.1.md`.

---

### ⚙️ Synthesis with the concept/instance layer

| Layer            | Prefix                | Schema                         | Example ID            | Example Edge                          |
| ---------------- | --------------------- | ------------------------------ | --------------------- | ------------------------------------- |
| Concept (family) | `sf.` / `it.` / `lc.` | `concept.schema.json`          | `sf.meditation`       | —                                     |
| Instance (node)  | `sn.` / `eq.` / `ev.` | `concept_instance.schema.json` | `sn.meditation.rank1` | `is_instance_of: sf.meditation`       |
| Meta / System    | `sys.`                | `system.schema.json`           | `sys.magic_system`    | `belongs_to_system: sys.magic_system` |

The prefixes aren’t just cosmetic—they’re part of your semantic schema.
They make your graph *linguistically self-documenting* and far easier to vectorize later.

---

So yes: **keep the long, explicit IDs**.
They make PHI both more *machine-readable* and more *story-aware*—a rare combo.

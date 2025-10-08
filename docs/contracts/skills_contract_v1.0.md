# Skills Contract (PHI)

**Title:** Skills Contract (PHI)
**Status:** Draft (v1.0)
**Updated:** 2025-10-08
**Linked Schemas:**

* `schemas/skill_family.schema.json`
* `schemas/skill_node.schema.json`
* `schemas/skills.schema.json`
  **Supersedes:** none (new file)

---

## 1. Purpose and Scope

This contract defines the canonical structure and validation rules for **Skills** within the Primal Hunter Index (PHI).
It unifies the conceptual framework — *Skill Families* and *Skill Nodes* — with provenance expectations, lineage semantics, and validation rules.

Schemas (`skill_family`, `skill_node`, `skills`) are **implementations** of this contract.
This document is the **normative source**: all schemas and validator tooling must conform to it.

---

## 2. Key Concepts

### 2.1 Skill Family (`sf.*`)

A **Skill Family** defines a *conceptual archetype* — the idea of a skill that can manifest in many forms.
It captures narrative identity, general description, and intent, but does not fix numerical parameters.

| Field          | Description                                                              |
| -------------- | ------------------------------------------------------------------------ |
| `family_id`    | Stable identifier, `sf.<slug>` (see ID Contract).                        |
| `name`         | Canonical human-readable name.                                           |
| `description`  | Narrative summary of purpose.                                            |
| `category`     | Broad grouping (`Combat Passive`, `Utility`, `Support`, etc.).           |
| `core_effects` | Optional baseline qualitative effects shared across all nodes.           |
| `source_ref[]` | First canonical appearance in text (must include scene ID + line range). |
| `record_log[]` | Standard audit history per Record Log Contract.                          |

Skill Families never reference specific characters or quantitative mechanics; they are **system archetypes**, not instances.

---

### 2.2 Skill Node (`sn.*`)

A **Skill Node** is a *manifestation* of a Skill Family — representing how a specific instance, rank, or evolution behaves in-world.

| Field          | Description                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| `node_id`      | Stable identifier, `sn.<slug>`.                                                |
| `family_id`    | Reference to parent `sf.*`.                                                    |
| `rarity`       | Controlled enum (`Inferior` → `Unique`).                                       |
| `effects`      | Canonical effect data — `stat_synergy`, `param_rule`, `proficiency_with`, etc. |
| `flavor`       | Narrative or flavor text tied to this node.                                    |
| `granted_by[]` | Array of structured sources per `granted_by.schema.json`.                      |
| `source_ref[]` | Provenance for this specific node (scene + line range).                        |
| `record_log[]` | Audit trail of creation, review, and schema updates.                           |
| `lineage`      | Optional object describing in-world evolution (see below).                     |

Each Node must reference exactly one Family by `family_id`.

---

### 2.3 Relationship Rules

1. **One Family → many Nodes.**
   A single `sf.*` can have multiple `sn.*` descendants (e.g. rank upgrades or divergent forms).

2. **Node Lineage Rules**

   Nodes represent discrete manifestations of a Skill Family.
   When a skill evolves, mutates, or changes classification, create a new Node.

   The new Node’s `lineage.evolves_from` field must reference its immediate predecessor Node.
   Nodes do not inherit mechanical parameters automatically, but lineage relationships allow downstream analysis and derived inference.

   **Lineage Object Definition**

   ```json
   "lineage": {
     "evolves_from": "sn.meditation.rank1",
     "related_to": ["sn.meditation.rank2_variant"],
     "notes": "Evolved through uncommon rank-up during tutorial sequence"
   }
   ```

   * `evolves_from`: string — `node_id` of immediate predecessor
   * `related_to`: array[string] — variant siblings or fusions
   * `notes`: string — free-form narrative comment

   Lineage describes **in-world evolution**, not editorial history.
   `record_log[]` remains reserved for audit and review metadata.

3. **Families cannot include character-specific details.**
   Those belong exclusively to Node level or timeline events.

4. **Family Persistence**

    Skill Families are **never deprecated** or merged in the archival sense.
    Each represents a stable conceptual archetype as it was understood when first introduced.

    When later canon revises, expands, or reinterprets a family concept:

    - Create a new Family (`sf.*`) if the System itself redefines the concept (e.g., Meditation splits into *Meditation* and *Transcendent Focus*).
    - Otherwise, append a `record_log[]` entry noting the revision context or reinterpretation.
    - Optionally link related concepts using `meta.related_to` to preserve semantic proximity.

    All earlier Families remain valid and queryable as historical artifacts of knowledge within the PHI timeline.

---

## 3. Provenance and Record Log Requirements

Provenance for families/nodes follows source_ref_contract_v1.1; placement rules follow the Provenance contract; low-certainty refs require human review before downstream use.

1. **Every Skill (Family or Node)** must include a non-empty `source_ref[]`.

   * For Families: cite the *first conceptual introduction.*
   * For Nodes: cite the *first explicit manifestation or upgrade.*
   * Fuzzy references (e.g. inferred evolutions) must include `type: "inferred"` and `inference_note`.

   *Provenance inside skill records captures the first canonical observation of that object.
   Subsequent discoveries or elaborations belong in character timelines, not as new `source_ref[]` entries.*

2. **Record Logs** track changes to both Families and Nodes.
   Each entry follows `record_log_contract_v1.1.md` and must include:

   * `entry_keys`: affected keys within the file
   * `method`: (`manual_seed`, `system_parse`, `inferred`, etc.)
   * `review_status`: (`pending`, `approved`, `rejected`)

3. **Inline provenance is forbidden** in aggregated skill registries (like `records/skills.json`).
   Provenance belongs in per-skill JSON files or `.meta.json` sidecars.

---

## 4. Validation and Enforcement Rules

| Validation Rule                                          | Description                                    |
| -------------------------------------------------------- | ---------------------------------------------- |
| `family_id` and `node_id` must follow ID Contract regex. | Enforced by `schemas/shared/id.schema.json`.   |
| Node `family_id` must exist in canon.                    | Validator cross-checks for matching `sf.*`.    |
| `source_ref[]` must contain `type: scene` or `inferred`. | No blank or malformed entries.                 |
| `effects.stat_synergy` values must be numbers.           | Object of numeric multipliers by stat name.    |
| `param_rule` must reference known stats/resources.       | Free-form formula permitted if lints cleanly.  |
| `granted_by[]` must use controlled type.                 | As defined in `granted_by.schema.json`.        |
| `additionalProperties: false`                            | Strict schema enforcement for all skill files. |

Validators (`validate_provenance.py`, `validate_all_metadata.py`) must confirm these constraints.

---

## 5. Anti-Patterns

❌ Do **not** reuse `sn.*` files to represent rank-ups — create new ones.
❌ Do **not** record System-wide archetypes (e.g. “All Skills Scale With Level”) as Families.
❌ Do **not** embed skill data directly in timelines; always reference the Node ID.
❌ Do **not** omit `record_log[]` for new entries, even if single-entry stub.
❌ Do **not** zero-fill stats that aren’t mentioned — omission implies “not applicable.”

---

## 6. Examples

**Skill Family**

```json
{
  "family_id": "sf.meditation",
  "name": "Meditation",
  "category": "Utility",
  "description": "A practice of focused stillness that improves mana flow and clarity.",
  "source_ref": [
    { "type": "scene", "scene_id": "01-02-01", "line_start": 50, "line_end": 55 }
  ]
}
```

**Skill Node**

```json
{
  "node_id": "sn.meditation.rank1",
  "family_id": "sf.meditation",
  "rarity": "Common",
  "effects": {
    "stat_synergy": { "Wis": 1.2 },
    "param_rule": "Mana cost = 10 - (Int * 0.5)"
  },
  "granted_by": [ { "type": "system", "name": "Tutorial Award" } ],
  "flavor": "Focus the mind; still the storm.",
  "lineage": {
    "evolves_from": null,
    "related_to": [],
    "notes": "Initial common variant granted in tutorial"
  },
  "source_ref": [
    { "type": "scene", "scene_id": "01-02-01", "line_start": 123, "line_end": 132 }
  ]
}
```

---

## 7. Future Extensions

* **Derived Knowledge Layer:** Generate `dk.*` records summarizing cross-character skill behavior (see `derived_knowledge_design.md`, planned).
* **Lineage Graph Queries:** Extend validation to traverse `lineage.evolves_from` and verify ancestry integrity.
* **Timeline Projection:** Integrate skill progression visualization into `projector.py` once timelines mature.

---

*Updated 2025-10-08*

# Skills Contract (PHI)

**Title:** Skills Contract (PHI)
**Status:** Draft (v1.0)
**Updated:** 2025-10-08
**Linked Schemas:**

- `schemas/skill_family.schema.json`
- `schemas/skill_node.schema.json`
- `schemas/skills.schema.json`
  **Supersedes:** none (new file)

---

## 1. Purpose and Scope

### Provenance rule
Canonical Skill **Family** (`sf.*`) and Skill **Node** (`sn.*`) payloads MUST NOT include `source_ref[]`. 
- Objective citations for families/nodes live in their sidecars (`.meta.json` / `.provenance.json`).
- Subjective discoveries and refinements live in character timelines as events with their own `source_ref[]`.


This contract defines the canonical structure and validation rules for **Skills** within the Primal Hunter Index (PHI).
It unifies the conceptual framework — *Skill Families* and *Skill Nodes* — with provenance expectations, lineage
semantics, and validation rules.

Schemas (`skill_family`, `skill_node`, `skills`) are **implementations** of this contract. This document is the
**normative source**: all schemas and validator tooling must conform to it.

---

## 2. Key Concepts

### 2.1 Skill Family (`sf.*`)

A **Skill Family** defines a *conceptual archetype* — the idea of a skill that can manifest in many forms. It captures
narrative identity, general description, and intent, but does not fix numerical parameters.

| Field          | Description                                                                          |
| -------------- | -------------------------------------------------------------------------------------|
| `family_id`    | Stable identifier, `sf.<slug>` (see ID Contract).                                    |
| `name`         | Canonical human-readable name.                                                       |
| `description`  | Narrative summary of purpose.                                                        |
| `category`     | Broad grouping (`Combat Passive`, `Utility`, `Support`, etc.).                       |
| `core_effects` | Optional baseline qualitative effects shared across all nodes.                       |
| `source_ref[]` | First canonical appearance in text (must include scene ID + line range in sidecar)   |
| `record_log[]` | Standard audit history per Record Log Contract. (In sidecar)                         |

Skill Families never reference specific characters or quantitative mechanics; they are **system archetypes**, not
instances.

---

### 2.2 Skill Node (`sn.*`)

A **Skill Node** is a *manifestation* of a Skill Family — representing how a specific instance, rank, or evolution
behaves in-world.

| Field          | Description                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| `node_id`      | Stable identifier, `sn.<slug>`.                                                |
| `family_id`    | Reference to parent `sf.*`.                                                    |
| `rarity`       | Controlled enum (`Inferior` → `Unique`).                                       |
| `effects`      | Canonical effect data — `stat_synergy`, `param_rule`, `proficiency_with`, etc. |
| `flavor`       | Narrative or flavor text tied to this node.                                    |
| `granted_by[]` | Array of structured sources per `granted_by.schema.json`.                      |
| `source_ref[]` | Provenance for this specific node (scene + line range). (In sidecar)           |
| `record_log[]` | Audit trail of creation, review, and schema updates.(In sidecar)               |
| `lineage`      | Optional object describing in-world evolution (see below).                     |

Each Node must reference exactly one Family by `family_id`.

---

### 2.3 Relationship Rules

1. **One Family → many Nodes.**
A single `sf.*` can have multiple `sn.*` descendants (e.g. rank upgrades or divergent forms).

2. **Node Lineage Rules**

Nodes represent discrete manifestations of a Skill Family. When a skill evolves, mutates, or changes classification,
create a new Node.

The new Node’s `lineage.evolves_from` field must reference its immediate predecessor Node. Nodes do not inherit
mechanical parameters automatically, but lineage relationships allow downstream analysis and derived inference.

**Rank upgrades vs within-rank evolution**

- **Rank/tier upgrades** recognised by the System create a **new node**. Record lineage via `lineage.evolves_from` on the new node and emit a timeline `skill_upgraded` event pointing from the old node to the new node.
- **Within-rank evolution** (no System rank change) stays on the **existing node**. Capture the improvement with a timeline `skill_evolved` event and an appropriate `knowledge_delta` overlay; no new node or lineage hop is created.

#### Lineage Object Definition

```json
"lineage": {
  "evolves_from": "sn.meditation.rank1",
  "notes": "Evolved through uncommon rank-up during tutorial sequence"
}
```

- `evolves_from`: string — `node_id` of immediate predecessor
- `notes`: string — free-form narrative comment

Lineage describes **in-world evolution**, not editorial history. `record_log[]` remains reserved for audit and review
metadata.

### Graph Links (Sidecar)

Skill Families and Nodes do not embed relationship edges in canonical payloads.  
Use the `.meta.json` sidecar `links[]` for lightweight graph edges:

- Allowed types: `upgrades_to`, `granted_by`, `related_to`, `derived_from`
- `target` references a stable ID; `reason` is optional and human-readable
- Links are deduplicated (unique `{type, target}`) and tooling should sort them for stable diffs
- Citations, if needed, live at the sidecar `source_ref[]` level

See: Graph Links Spec v1.0.

1. **Families cannot include character-specific details.**
Those belong exclusively to Node level or timeline events.

1. **Family Persistence**

Skill Families are **never deprecated** or merged in the archival sense. Each represents a stable conceptual archetype
as it was understood when first introduced.

When later canon revises, expands, or reinterprets a family concept:

- Create a new Family (`sf.*`) if the System itself redefines the concept (e.g., Meditation splits into *Meditation* and *Transcendent Focus*).
- Otherwise, append a `record_log[]` entry noting the revision context or reinterpretation.
- Optionally link related concepts using `meta.related_to` to preserve semantic proximity.

All earlier Families remain valid and queryable as historical artifacts of knowledge within the PHI timeline.

---

## 3. Provenance and Record Log Requirements

Provenance for families/nodes follows source_ref_contract_v1.1; placement rules follow the Provenance contract; low-
certainty refs require human review before downstream use.

1. **Every Skill (Family or Node)** must include a non-empty `source_ref[]`.

   - For Families: cite the *first conceptual introduction.*
   - For Nodes: cite the *first explicit manifestation or upgrade.*
   - Fuzzy references (e.g. inferred evolutions) must include `type: "inferred"` and `inference_note`.

   *Provenance inside skill records captures the first canonical observation of that object.
Subsequent discoveries or elaborations belong in character timelines, not as new `source_ref[]` entries.*

2. **Record Logs** track changes to both Families and Nodes.
Each entry follows `record_log_contract_v1.1.md` and must include:

- `entry_keys`: affected keys within the file
- `method`: (`manual_seed`, `system_parse`, `inferred`, etc.)
- `review_status`: (`pending`, `approved`, `rejected`)

1. **Inline provenance is forbidden** in aggregated skill registries (legacy `records/skills.json`).
Provenance belongs in per-skill JSON files under `records/skills/` or accompanying `.meta.json` sidecars.

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

- ❌ Do **not** reuse `sn.*` files to represent rank-ups — create new ones.
- ❌ Do **not** record System-wide archetypes (e.g. “All Skills Scale With Level”) as Families.
- ❌ Do **not** embed skill data directly in timelines; always reference the Node ID.
- ❌ Do **not** omit `record_log[]` for new entries, even if single-entry stub.
- ❌ Do **not** zero-fill stats that aren’t mentioned — omission implies “not applicable.”

---

## 6. Examples

### Skill Family Example

```json
{
  "family_id": "sf.meditation",
  "name": "Meditation",
  "category": "Utility",
  "description": "A practice of focused stillness that improves mana flow and clarity."
}
```

### Skill Node Example

```json
{
  "node_id": "sn.meditation.rank1",
  "family_id": "sf.meditation",
  "rarity": "Common",
  "effects": {
    "stat_synergy": { "Wis": 1.2 },
    "param_rule": "Mana cost = 10 - (Int * 0.5)"
  },
  "flavor": "Focus the mind; still the storm.",
  "lineage": {
    "evolves_from": null,
    "notes": "Initial common variant granted in tutorial"
  }
}
```

Companion sidecar (`records/skills/sn.meditation.rank1/meta.json`):

```json
{
  "id": "sn.meditation.rank1",
  "record_log": [
    { "action": "added", "by": "assistant", "date": "2025-10-08" }
  ],
  "source_ref": [
    { "type": "scene", "scene_id": "01.02.01", "line_start": 120, "line_end": 130 }
  ],
  "links": [
    { "type": "granted_by", "target": "ev.jake.01.02.01.skill_acquired_meditation", "reason": "Tutorial award" },
    { "type": "upgrades_to", "target": "sn.meditation.rank2" }
  ]
}
```

---

## 7. Future Extensions

- **Derived Knowledge Layer:** Generate `dk.*` records summarizing cross-character skill behavior (see `derived_knowledge_design.md`, planned).
- **Lineage Graph Queries:** Extend validation to traverse `lineage.evolves_from` and verify ancestry integrity.
- **Timeline Projection:** Integrate skill progression visualization into `projector.py` once timelines mature.

---

### Related Docs

- [Skills Entry Runbook](../runbooks/skills_entry_runbook.md)
- [Skills Structure Runbook](../runbooks/skills_structure_runbook.md)
- [Skills Overview Design](../design/skills_overview_design.md)
- [ID Contract](./id_contract_v1.1.md)

---

**Last updated:** 2025-10-08

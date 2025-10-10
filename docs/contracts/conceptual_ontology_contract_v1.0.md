# 🧩 Conceptual Ontology Contract (PHI)

**Title:** PHI Conceptual Ontology Contract
**Status:** Living (v1.0)
**Updated:** 2025-10-09
**Purpose:** Defines how entities, concepts, and relationships form the semantic backbone of the Primal Hunter Index (PHI).

---

## 1. Purpose

This contract defines how PHI represents meaning.
It explains the distinction between *concepts*, *instances*, and *relationships*, and how those together build a dynamic knowledge graph capable of both factual precision and generative flexibility.

### Provenance rule
Concepts and instances do not embed `source_ref[]` in their canonical payloads. 
- Use sidecars for objective citations and audit trails.
- Use character timelines for subjective observations or knowledge changes.

---

## 2. Core Definitions

### 2.1 Concepts (`cf.*`)

* **What they are:** Archetypes, abstractions, or families of things.
  They describe *what kind of idea* something is — a pattern, not an occurrence.

* **Examples:**

  * `cf.skill` — the idea of a skill as a mechanic.
  * `cf.magic_system` — the underlying rules governing affinities.
  * `cf.teleportation` — the general ability to relocate instantly.

* **Schema:** `concept.schema.json`

  * `concept_id` (`cf.*`)
  * `name`
  * `category` (skill, class, item, race, location, system, etc.)
  * `description`
  * `source_ref[]` — where this concept first appears
  * `record_log[]` — editorial record of updates

Concepts never store character-specific data or world instances; they are the “families.”

---

### 2.2 Concept Instances (`ci.*`)

* **What they are:** Concrete manifestations of a concept — a skill node, an item copy, a location state, etc.
  They exist in time and can differ between observers.

* **Examples:**

  * `ci.sn.meditation.rank1` — Jake’s initial Meditation skill.
  * `ci.sf.teleportation` — the teleportation ability as used by a specific character.

* **Schema:** `concept_instance.schema.json`

  * `instance_id` (`ci.*`)
  * `concept_id` — parent concept
  * `owner` — who or what possesses or manifests it
  * `properties` — domain-specific fields (effects, rarity, cooldowns)
  
Sidecars carry tags/links, provenance, and record logs; canonical instance payloads remain quote-free.

---

## 3. Relationships (Edges)

All higher-order meaning is defined by **typed edges** between nodes.
An edge record looks like this:

```json
{
  "relation_id": "rel.001",
  "source_id": "sn.meditation.rank1",
  "target_id": "sf.meditation",
  "predicate": "is_instance_of"
}
```

### Sidecar Graph Links (pragmatic edges)

Use `.meta.json` `links[]` to annotate local, typed edges for convenience:
`upgrades_to`, `granted_by`, `related_to`, `derived_from`.

These sidecar links are prefix-agnostic (validated via the shared ID schema), deduplicated by `{type, target}`, and do not carry per-link provenance (cite at the sidecar level when needed).  
Editorial history links (e.g., `replaces`, `split_from`, `merged_into`) continue to live under the ID and Record Log contracts.

See: Graph Links Spec v1.0.

### 3.1 Core Predicates

| Predicate              | Direction           | Purpose                                                              |
| ---------------------- | ------------------- | -------------------------------------------------------------------- |
| `is_instance_of`       | instance → concept  | Connects a specific manifestation to its archetype.                  |
| `is_specialization_of` | concept → concept   | Defines lateral refinement within the same tier.                     |
| `upgrades_from`        | node → node         | Links evolution stages of the same concept family.                   |
| `belongs_to_system`    | node → concept      | Ties a node or concept into a broader mechanic (e.g., Magic System). |
| `influenced_by`        | node → node/concept | Expresses epistemic or causal influence.                             |
| `contradicts`          | fact → fact         | Marks mutually exclusive or paradoxical statements.                  |
| `inherits_from`        | node → node         | Marks mechanic or data inheritance.                                  |
| `expressed_by`         | concept → entity    | Binds abstract laws to tangible actors (characters, items, places).  |

Predicates *are* the type system.
You don’t hard-type “SkillNode” — its pattern of edges defines its nature.

---

## 4. Emergent Semantics

1. **Deterministic meaning:** Each node has fixed, schema-verified data.
2. **Contextual meaning:** Relationships form the contextual layer — tone, causality, narrative.
3. **Vector grounding:** When embedded, each predicate defines a semantic dimension:

   * `is_instance_of` → abstraction depth
   * `upgrades_from` → temporal/evolution vector
   * `influenced_by` → causal/epistemic flow
   * `belongs_to_system` → domain clustering

Meaning is not stored *in* text but *between* nodes.

---

## 5. Ontological Hierarchy

Everything is both a *thing* and a *kind of thing*.
Concepts may be instances of higher-order concepts:

```
cf.skill ── is_instance_of ──► cf.magic_system
cf.magic_system ── is_instance_of ──► cf.narrative_mechanic
```

This forms a **lattice**, not a tree: entities can have multiple parents and cross-domain links.

---

## 6. Design Philosophy

* Facts in PHI are literal and unambiguous.
* Relationships are contextual and “dreamlike.”
* The system separates:

  * **Ontology:** what exists (truth layer)
  * **Phenomenology:** how it’s perceived (context layer)
* Generation happens within the graph’s physics; teleportation is valid if the dataset encodes it as true.

---

## 7. Validation Rules

1. Every `concept_instance` must reference an existing `concept`.
2. Every edge must use a defined predicate from the predicate registry.
3. Cycles are allowed only when marked as paradox (`contradicts`).
4. Provenance (`source_ref[]`) is mandatory for all nodes and edges.

---

## 8. Example Slice

```json
// concept
{
  "concept_id": "cf.teleportation",
  "name": "Teleportation",
  "category": "Skill",
  "description": "Instant relocation through spatial folding.",
  "source_ref": [{"scene_id": "01.02.01", "line_start": 20, "line_end": 25}]
}

// instance
{
  "instance_id": "ci.sn.teleportation.rank1",
  "concept_id": "cf.teleportation",
  "owner": "pc.jake",
  "properties": {"cooldown": "5s"},
  "source_ref": [{"scene_id": "01.03.02", "line_start": 40, "line_end": 50}]
}

// relationship
{
  "relation_id": "rel.004",
  "source_id": "ci.sn.teleportation.rank1",
  "target_id": "cf.teleportation",
  "predicate": "is_instance_of"
}
```

---

## 9. Why It Works

This model gives you:

* A deterministic symbolic graph (for truth).
* A probabilistic embedding layer (for creativity).
* A unified type system defined by relationships.
* A direct path to vectorization and generative grounding.

---
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
ev.jake.01.02.01.a         # timeline event
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

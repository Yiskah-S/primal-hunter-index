# Skill Structure Runbook

**Status:** Living  
**Updated:** 2025-10-08  
**Linked Schemas:** `schemas/skill_family.schema.json`, `schemas/skill_node.schema.json`  
**Linked Contract:** [skills_contract_v1.0.md](../contracts/skills_contract_v1.0.md)  
**Source:** Expanded from `docs/runbooks/context_summary.md#skills-are-families-not-constants`

---

## 1. Conceptual Overview — Skills Are Families, Not Constants

A *skill family* (`sf.*`) defines the conceptual identity of a skill — its purpose, nature, and intended mechanical role
in the world. A *skill node* (`sn.*`) represents a specific manifestation of that family as observed in canon — whether
that’s a rank-up, evolution, or personalized variant.

Each node inherits conceptual lineage from exactly one family but can diverge in its parameters, effects, rarity, or
flavor. This two-tier design lets us model evolution and variant behavior without overwriting history.

> “A `skill_family` is the idea. A `skill_node` is a specific expression of that idea within a character’s progression.”
> — *Context Summary, design section*

---

## 2. Data Flow and Provenance

Stage 1 — *Skill concept first appears* • File: `records/skills/sf.*.json` • Provenance: `source_ref[]` cites first
canonical mention.

Stage 2 — *Character acquires skill* • File: `records/<character>/timeline.json` • Provenance: timeline event with
`type: skill_acquired`.

Stage 3 — *Variant or evolution emerges* • File: new `sn.*.json` under `records/skills/` • Provenance: `record_log[]`
shows relation to parent node.

Stage 4 — *Narrative observations refine details* • File: `.meta.json` sidecars update certainty and review notes. •
Provenance: validated by `validate_provenance.py`.

All provenance chains begin in the **scene index** and flow through the **timeline**. Every skill node or family must
include at least one `source_ref` entry citing the exact canonical line range.

---

## 3. When to Create a New Skill Node

Create a new node when: • The function or mechanic changes in a material way. • Two characters manifest the same family
differently. • The skill evolves, fuses, or transforms. • The System assigns a new rank, rarity, or modifier.

Do **not** create a new node when: • Only numeric scaling shifts due to level-up. • The same node is re-mentioned
without change. • Flavor text expands without mechanical change.

These rules prevent node inflation and preserve the clarity of the skill graph.

---

## 4. Structure and Schema Integration

Example `skill_node` entry:

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
  "source_ref": [
    {
      "type": "scene",
      "scene_id": "01.02.01",
      "line_start": 123,
      "line_end": 132
    }
  ]
}
```

Each node and family is validated by schema and provenance tools: • `make validate` checks schema compliance. • `make
validate-provenance` ensures no inline source_ref violations. • `.meta.json` and `.review.json` sidecars track human
verification.

---

## 5. Review and Maintenance Notes

• Keep `sf.*` minimal — they should capture only the *concept*, not character-specific data. • Treat `sn.*` as per-
manifestation — record who, where, and how the skill appeared. • When canon reveals a new variant, never edit the old
node; add a new one linked by `record_log[]`. • Keep schema alignment by re-running validation after any new node or
family is introduced. • Ensure `source_ref` always ties back to real scene IDs and line ranges.

---

**Summary:**
This runbook explains *how* to represent skill families and nodes inside the repository. The companion
`skill_hierarchy_contract_v1.0.md` will define *why* the system enforces those relationships and the exact schema rules
that back them.

---

### Related Docs

- [Skills Contract](../contracts/skills_contract_v1.0.md)
- [Skills Entry Runbook](./skills_entry_runbook.md)
- [Skills Overview Design](../design/skills_overview_design.md)

---

**Last updated:** 2025-10-08

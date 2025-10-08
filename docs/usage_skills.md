# Skill Family and Node Usage Guide
> **Status:** Canonical usage guide  
> **Linked schemas:** `schemas/skill_family.schema.json`, `schemas/skill_node.schema.json`  
> **Linked contracts:** `docs/contracts/skill_hierarchy_contract_v1.0.md` *(draft pending)*  
> **Last updated:** 2025-10-08  
> **Source:** Expanded from `docs/runbooks/context_summary.md#skills-are-families-not-constants`

---

## 🧩 1. Conceptual Overview — Skills Are Families, Not Constants

> “A `skill_family` is the *idea*.  
> A `skill_node` is a *specific expression* of that idea within a character’s progression.”  
> — *Context Summary, design section*

In the Primal Hunter Index, a **Skill Family** (`sf.*`) defines the *conceptual identity* of a skill: its purpose, nature, and intended mechanical role in the world.  
A **Skill Node** (`sn.*`) represents a *particular manifestation* of that family as observed in canon — whether that’s a rank-up, evolution, or personalized variant.

Each `skill_node` inherits conceptual lineage from exactly one `skill_family`, but may diverge in:

- parameters (`param_rule` fragments)  
- effects (`stat_synergy`, `resource_change`)  
- rarity or classification  
- flavor / narrative description

This two-tier system allows the Index to model skill evolution and variant behavior without overwriting history.

---

## 🧭 2. Data Flow and Provenance

| Stage | Event | Data File | Provenance |
|:--|:--|:--|:--|
| 1 | Skill concept first appears | `records/skills/sf.*.json` | `source_ref[]` cites first canonical mention |
| 2 | Character acquires skill | `records/<character>/timeline.json` | Timeline event `type: skill_acquired` |
| 3 | Variant or evolution emerges | new `sn.*.json` under `records/skills/` | `record_log[]` shows relation to parent node |
| 4 | Narrative observations refine details | `.meta.json` sidecars update certainty / review | validated by `validate_provenance.py` |

All provenance chains begin in the **scene index** and flow through the **timeline**.  
Every skill node or family must be backed by one or more `source_ref` entries citing the exact line range in canon.

---

## 🧱 3. When to Create a New Node

A new `skill_node` **must** be created when any of the following occur:

✅ **Material change in function** — effect, cost, or scaling formula alters  
✅ **Character divergence** — two entities manifest the same family differently  
✅ **Evolution or fusion** — canonical mention of transformation or merging  
✅ **System designation** — new rank, rarity, or modifier explicitly named  

Do **not** create a new node when:

❌ Only numerical values shift due to leveling  
❌ The same form is re-mentioned without change  
❌ Flavor text elaborates but no new mechanics appear  

These rules prevent exponential node inflation and preserve meaningful graph structure.

---

## 🔗 4. Structure and Schema Integration

Example `skill_node`:

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
      "scene_id": "01-02-01",
      "line_start": 123,
      "line_end": 132
    }
  ]
}

# 🏷 Tagging Outline – PHI (Summary View)

**ADR-0001:** Split status vs tag_role for tags
**Date:** 2025‑10‑06
**Status:** Accepted
**Context:** …
**Decision:** …
**Consequences:** …

This file is a quick checklist / cheat sheet for tagging logic.
For full rules, see [`tagging_contract_v0.4.md`](../contracts/tagging_contract_v0.4.md)

---

---

## ✅ Core Workflow

- Tags are lowercase snake_case (e.g., `archers_eye`, `malefic_viper`)
- Tags used in canon must exist in `tag_registry.json`
- Registry tracks:
  - `status`: "approved" / "candidate" / "rejected"
  - `allow_inferred`: true/false

## 🔁 Tagging Pipeline

- Scrape raw tags → `tag_candidates.json`
- Review + promote → `tag_registry.json`
- Canon uses only `"approved"` tags
- `allow_inferred: true` allows LLM/heuristic suggestion
- Canon tags must be backed by strong context

---

## 📌 Examples

| Use Case                       | Tags                                   |
|--------------------------------|----------------------------------------|
| Stealth skill used             | `stealth`, `basic_archery`             |
| Soul-based void event          | `void_affinity`, `soul_damage`         |
| Romance between characters     | `romantic_scene`, `social_scene`       |
| Lore about meditation          | `meditation`, `skill_lore`, `system`   |

---

## 🧪 Tag Validation Rules

- All scene/timeline tags must match the registry
- Registry must validate against `tag_registry.schema.json`
- Scene tags validated by `$ref: tags.schema.json`

**Superseded By:** [`contracts/tagging_contract_v0.4.md`](../contracts/tagging_contract_v0.4.md)  
**Decision Summary:** Tag lifecycle (`status`) is decoupled from purpose (`tag_role`)
to support heuristic vs canonical flows in tagging pipeline v0.4. For implementation details, see
[`tagging_contract_v0.4.md`](../contracts/tagging_contract_v0.4.md) and
[`provenance_contract_v2.0.md`](../contracts/provenance_contract_v2.0.md) for how tags are quote-backed.

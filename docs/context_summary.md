# 📦 PHI Context Summary: What We Actually Decided

Everything below is confirmed canon for *your data model and story engine*. This is the stuff you don’t have to re-debate on Monday. Paste it into your brain (or Codex).

---

## 🧱 Core Data Model

### ✅ Skills are *families*, not constants
- `skill_family`: The core idea (e.g. Meditation)
- `skill_node`: A variant or evolution (e.g. Meditation [Common])
- Characters follow a *path* through the graph of nodes
- Multiple characters = multiple paths

---

### ✅ Parameters are fuzzy rules, not fixed numbers
- Param rules go in nodes as **heuristic descriptions** or loose formulas
- Observed values go in character timelines
- Don’t hardcode costs into skills. Track them as observed.

---

### ✅ Canon = Quote-backed, not boolean
- `canon: true` is **soft-deprecated**
- If a record has `source_ref`, it’s canon
- If it’s in `fixtures/` or has no provenance, it’s test or proposal

---

### ✅ Provenance lives in the **event**, not in the data blob
- `source_ref[]` = scene_id + line range (+ optional quote)
- Stored only at points where the character learned or observed a change

---

### ✅ Character state is logged, not snapshot
- State is not tracked per-chapter
- Instead, you store events like:
  - `skill_acquired`
  - `skill_upgraded`
  - `param_observed`
  - `equip_changed`
- Use a `projector.py` to simulate full state at any scene by replaying events

---

### ✅ Separate structure from content
| Layer | What it tracks |
|-------|----------------|
| `skill_family` | Name, flavor, tags — no stats |
| `skill_node` | Variant rules, prereqs, potential upgrades |
| `timeline.json` | Per-character event logs (state changes with context) |
| `record_log[]` | File-level meta for audit/review |
| `source_ref[]` | Scene-backed quotes that justify each data point |

---

## 📂 File System Philosophy

- `records/` = Canon data
- `fixtures/` = Test inputs
- `sandbox/` = Scratch or dev data
- `z_notes/` = Personal planning
- `z_codex_context/` = Memory hydration for Codex/GPT

---

## 🔧 Event Types You’ve Locked In

- `skill_acquired`
- `skill_upgraded`
- `param_observed`
- `class_changed`
- `tier_changed`
- `equip_changed`
- `affinity_changed`
- `domain_event` (planned)
- `worldscale_operation` (planned)
- `profession_milestone` (planned)

---

## 🚧 Philosophy, Not Just Structure

- This project exists to let you **write quote-backed stories about alternate protagonists**
- Zogarth wrote the world. You’re writing the other books inside it.
- Schemas exist to serve story generation — not block it.
- Every piece of data should help answer:  
  > *What could Arnold/Miranda/X have done, in a way that feels real, earned, and system-consistent?*

---

# Primal Hunter Index Project (PHI)

This project aims to:
- Reverse-engineer the PH universe’s systems and logic
- Track skills, characters, and progression through schema-driven timelines
- Generate alternate-canon stories (e.g., Arnold POV) that are quote-backed and tonally consistent

## Quick Start

- See `docs/context_summary.md` for schema design rules
- See `docs/tone_contract.md` for storywriting tone constraints
- Codex + GPT use these to scaffold proposals and outputs

All data in `records/` is structured and quote-backed.
All test data lives in `fixtures/` or `sandbox/`.

This is not a wiki.
This is a simulation engine for narrative logic.



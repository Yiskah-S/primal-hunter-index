<!--
───────────────────────────────────────────────────────────────────────────────
📘 PROJECT CONTEXT ANCHOR
───────────────────────────────────────────────────────────────────────────────
This document summarizes the *canonical design decisions* that define the PHI
data model and provenance logic. It is NOT a schema or contract; it provides 
orientation for contributors, validators, and Codex prompts.
───────────────────────────────────────────────────────────────────────────────
-->

# 📦 PHI Context Summary: The Core Model You Don’t Re-Debate

Everything below is confirmed canon for the **Primal Hunter Index (PHI)** data model  
and story engine. These are the rules your schemas, validators, and Codex all align on.

---

## 🧱 1. Core Data Model

### ✅ Skills are *families*, not constants
- `skill_family` — the conceptual root (e.g., *Meditation*)
- `skill_node` — a specific form or rank (e.g., *Meditation [Common]*)
- Characters progress along *paths* through the skill graph  
- Multiple characters may share a family but have distinct node trajectories

---

### ✅ Parameters are *fuzzy rules*, not fixed numbers
- Node files store heuristic or formula-style parameter logic  
  *(e.g., “cost scales with Willpower²”)*  
- Observed values are logged in character timelines
- Never hardcode costs or cooldowns in canon; treat them as observed behavior

---

### ✅ Canon = quote-backed, not boolean
- `canon: true` is **soft-deprecated**
- Provenance via `source_ref[]` is what truly proves canon
- `canon: true` may remain as a convenience filter for query and search tools
- Entries without provenance (or in `fixtures/`) are considered *non-canonical scaffolding*

---

### ✅ Provenance lives in the **event**, not the blob
- `source_ref[]` = `{ scene_id, line_start, line_end, quote }`
- Stored only in:
  - `timeline.json` events (when something happens)
  - `.meta.json` sidecars (for global facts)
- Canon records remain lightweight, quote-free reference material

---

### ✅ Character state is logged, not snapshotted
- No per-chapter full states — only *events*
- Event types include:
  - `skill_acquired`
  - `skill_upgraded`
  - `param_observed`
  - `equip_changed`
  - `class_changed`
  - `tier_changed`
  - *(and others below)*
- Use `tools/projector.py` to replay timelines and compute “state at scene X”

---

### ✅ Structure is separate from content

| Layer | What it represents |
|-------|--------------------|
| `skill_family` | Concept and flavor text only |
| `skill_node` | Rule fragments, prereqs, upgrade links |
| `timeline.json` | Per-character events (facts with context) |
| `.meta.json` | File-level audit, provenance, `record_log[]` |
| `source_ref[]` | Scene-level justification (quotes and spans) |

---

## 📂 2. File System Philosophy

| Folder | Purpose |
|---------|----------|
| `records/` | Canon data (quote-backed) |
| `fixtures/` | Test scaffolding and prototype inputs |
| `sandbox/` | Temporary experimental data |
| `z_notes/` | Personal notes and scratchpads |
| `z_codex_context/` | Memory hydration + GPT prompt context |

---

## ⚙️ 3. Event Type Registry (Confirmed)

| Event Type | Description |
|-------------|-------------|
| `skill_acquired` | Character gains a new skill node |
| `skill_upgraded` | Node advances or evolves |
| `param_observed` | Stat, duration, or cost observed in-scene |
| `class_changed` | Character gains or swaps class |
| `tier_changed` | Grade or tier advancement |
| `equip_changed` | Equipment added, removed, or modified |
| `affinity_changed` | Elemental or energy alignment shift |
| `domain_event` | Large-scale or world-spanning phenomenon |
| `worldscale_operation` | Realm-affecting system action |
| `profession_milestone` | Advancement within a crafting/profession track |

💡 *More may be added later, but these cover all core progression mechanics.*

---

## 🚧 4. Philosophy, Not Just Structure

This project exists to let you **write quote-backed, system-consistent stories**  
about alternate protagonists inside the *Primal Hunter* universe.

Zogarth wrote the world.  
You’re writing the *other books within it.*

### Guiding Principles

- Schemas exist to serve *story generation*, not block it
- Every canonical record must support narrative logic — not just data lookup
- Provenance exists so Codex (and you) can **justify every claim** in-universe
- The core design question behind every schema change should be:  
  > “Does this help us write what Arnold/Miranda/X could have done —  
  > in a way that feels *real*, *earned*, and *system-consistent*?”

---

## 🧭 5. Quick Start for New Contributors

**1. Read these first:**
- [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)
- [`contracts/id_contract.md`](../contracts/id_contract.md)
- [`contracts/record_log_contract.md`](../contracts/record_log_contract.md)

**2. Understand the data flow:**
1. Scene introduces a new skill → timeline event logged  
2. Canon record (`sf.*`, `sn.*`) created or updated  
3. `.meta.json` sidecar records provenance + review  
4. `projector.py` recomputes character state  
5. Tools validate and enforce cross-refs by ID

**3. Never edit canon facts without updating their provenance.**  
The quote is the proof.

---

## 📎 Related Docs

| Category | File |
|-----------|------|
| **Contracts** | [`provenance_contract.md`](../contracts/provenance_contract.md) · [`source_ref_contract.md`](../contracts/source_ref_contract.md) · [`record_log_contract.md`](../contracts/record_log_contract.md) · [`id_contract.md`](../contracts/id_contract.md) |
| **Design DDRs** | [`storage_layout.md`](../design/storage_layout.md) · [`pipeline_flow.md`](../design/pipeline_flow.md) · [`provenance_architecture.md`](../design/provenance_architecture.md) |
| **Runbooks** | [`provenance_workflow.md`](../runbooks/provenance_workflow.md) · [`projector_usage.md`](../runbooks/projector_usage.md) |
| **Tone & Story Rules** | [`tone_contract.md`](../contracts/tone_contract.md) |

---

> 🧠 **Reminder:**  
> This repository is not a wiki — it’s a **simulation engine for narrative logic.**  
> Everything quote-backed is canon; everything else is just scaffolding.

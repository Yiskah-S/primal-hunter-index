Perfect — yes, we’re still solid on `skills_overview_design.md`.
That doc covers *how the skill architecture works conceptually* — the family/node hierarchy, why it exists, and how it serves the epistemic engine.

So now let’s give you the matching **`context_summary_design.md`** — the “grand design preamble” that explains how PHI thinks about knowledge, provenance, and narrative logic.

Here’s the complete version (ready to drop in `docs/design/context_summary_design.md`):

---

# Context Summary (Design Overview)

**Title:** Context Summary (PHI Design Overview)
**Status:** Living Draft
**Updated:** 2025-10-08
**Purpose:** Foundation document describing PHI’s epistemic and structural worldview.
**Linked Contracts:**

* `docs/contracts/provenance_contract_v2.0.md`
* `docs/contracts/record_log_contract_v1.1.md`
* `docs/contracts/skills_contract_v1.0.md`

---

## 🧭 1. What PHI Is (and Isn’t)

The **Primal Hunter Index (PHI)** is *not* a wiki, a glossary, or a data dump of lore.
It’s a **knowledge-graph architecture** for encoding how information *exists, is known, and is learned* inside the *Primal Hunter* universe.

PHI treats the story world as a multi-layer system of knowledge:

1. **Diegetic layer:** what exists objectively in the world (skills, dungeons, events).
2. **Epistemic layer:** what each character *knows or believes* about that world at any moment.
3. **Temporal layer:** when those facts or beliefs change in the narrative.

By combining these, PHI creates the scaffolding needed for a generative AI to reason about *who knows what, and when* — something standard LLMs fail at because they flatten everything into omniscient narration.

---

## 🧩 2. Core Principles

**1️⃣ Provenance is non-negotiable.**
Every fact is backed by a `source_ref[]` — the *when, where, and by whom* of its observation.
No statement can exist in canon without textual grounding.

**2️⃣ Records are snapshots, not mutable truths.**
Files under `records/` represent immutable observations — “this is what was known, at this point.”
New discoveries add new records; they never overwrite the old.

**3️⃣ Timelines model epistemic growth.**
Each character’s timeline logs events like “skill acquired,” “insight gained,” or “belief corrected.”
From these events, the system can reconstruct that character’s worldview at any moment in the story.

**4️⃣ Sidecars carry meta-context.**
`.meta.json`, `.review.json`, and `.provenance.json` store audit data, reviewer notes, and traceable source maps.
They preserve process history without polluting the canon layer.

**5️⃣ Documentation precedes schema.**
PHI’s law of creation: *docs → schema → code → data.*
Every structure begins as a design contract before a single line of JSON exists.

---

## 🧠 3. The Narrative Model

Each canonical record lives at the intersection of:

* **What exists in the story** (diegetic),
* **Who knows about it** (epistemic),
* **When it was observed** (temporal).

The result is a *time-indexed graph of knowledge*, where:

| Concept            | Stored In                                 | Represents                                       |
| ------------------ | ----------------------------------------- | ------------------------------------------------ |
| Skill family       | `records/skills/sf.*`                     | The idea of a skill.                             |
| Skill node         | `records/skills/sn.*`                     | A specific observed manifestation.               |
| Character timeline | `records/characters/<name>/timeline.json` | That character’s evolving knowledge and actions. |
| Provenance sidecar | `.provenance.json`                        | Scene → fact mapping for traceability.           |

Together, these elements allow the Index to simulate how characters learn about their world — a structured “theory of mind” scaffold for narrative AI.

---

## 🧱 4. Why This Matters

LLMs can mimic tone and syntax, but they struggle with *temporal epistemic reasoning*:
tracking partial knowledge, forgotten facts, evolving beliefs, or simultaneous perspectives.

PHI solves that by encoding:

* **What’s true** (objective world state)
* **Who knows it** (character-specific knowledge)
* **When it changes** (narrative order)

This turns *story canon* into a **reconstructable system of knowledge evolution** — teachable to an LLM via retrieval-augmented generation or fine-tuning.

---

## 🔗 5. Linked Design Layers

* `skills_overview_design.md` — expands the “skills as families” architecture.
* `provenance_contract_v2.0.md` — defines the proof chain for every fact.
* `record_log_contract_v1.1.md` — captures when and how data changes.
* `skills_contract_v1.0.md` — codifies how skills inherit and evolve.
* `timeline_contract_v1.0.md` (planned) — defines how epistemic state is reconstructed across time.

---

## 🧩 6. Future Directions

* Extend epistemic modeling to factions, gods, and world systems (not just characters).
* Introduce inference-level provenance (`inferred_from[]`) for cross-character learning.
* Implement automated snapshot diffs (`projector.py`) for reconstructing “knowledge at scene.”

---

**This project encodes cognition, not content.**
The PHI isn’t a repository of facts — it’s a *simulation of knowing.*

---

Would you like me to also generate a quick header block you can paste into the `docs/README.md` “Docs Map” section for this new file so it shows up cleanly there?

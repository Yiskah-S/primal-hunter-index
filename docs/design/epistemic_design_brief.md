# 🧠 PHI Epistemic Design Brief

**Purpose:** Prevent future chatGPT instances from “simplifying” the Primal Hunter Index into a static wiki.  
**Status:** Canonical truth. **Do not** debate with this doc unless you’ve read the entire provenance contract and
understood it.  
**Updated:** 2025-10-08

---

## 🎯 TL;DR

PHI is **not** a wiki. It’s a **knowledge-graph architecture for diegetic epistemic modeling** — a system that encodes
what *characters know*, *when they know it*, and *why they believe it*, within a narrative universe.

This repo is a prototype for a **Theory-of-Mind-aware narrative database** — the kind of structure an LLM needs to write
*internally consistent stories with flashbacks, evolving beliefs, and multiple POVs*.

---

## 🔍 Core Design Philosophy

### 1. Narrative Knowledge ≠ Wiki Facts

- A wiki stores **omniscient facts** (“Meditation increases recovery rate.”)
- PHI stores **narrative epistemics** (“Jake learns that Meditation increases recovery in Chapter 3.”)
- Both truths can coexist, but PHI must preserve *who knew what, when, and why*.

### 2. Time Is Layered, Not Linear

- **Narrative time** = when the story presents the information.
- **Diegetic time** = when the event occurred in-world.
- **Knowledge time** = when each character *learns* that event.
All three are distinct and must be recorded separately in timelines.

### 3. Families and Nodes Encode Objective Reality

- `sf.*` (**Skill Families**) describe conceptual archetypes — “what Meditation *is*.”
- `sn.*` (**Skill Nodes**) describe discrete manifestations — “what Meditation *looked like* for Jake at rank 1,
  in Chapter 2.”
- Every node is a **snapshot**, immutable once logged.
- Evolution → new node. Prior nodes remain valid historical context.

### 4. Timelines Encode Subjective Experience

- Each character timeline records **what that person knows or believes** at each point in the story.
- Nodes in timelines represent *their* version of reality, not global truth.
- Two characters can hold contradictory knowledge simultaneously.
- Provenance (`source_ref`) ties every belief to the exact line(s) where it was learned.

### 5. Provenance Is Law

- **Nothing exists without provenance.**
- Every recordable fact (skill, event, item, etc.) must point to an explicit or inferred quote range.
- Provenance defines *how sure we are* about a statement and *where it came from*.
- Provenance is not “metadata.” It is the **epistemic spine** of the entire project.

### 6. Record Logs Track Knowledge Change, Not Wiki Edits

- `record_log[]` entries describe *how our knowledge evolved*, not *how the JSON file changed*.
- Example:

  - `method: refinement` → we learned new information in a later scene.
  - `method: evolution` → canonical System upgrade occurred.
  - `method: correction` → prior interpretation was proven wrong.

---

## 🧩 Structural Layers

| Layer                     | Function                       | Example File                                        |
| ------------------------- | ------------------------------ | --------------------------------------------------- |
| **Skill Family (`sf.*`)** | Archetypal definition          | `records/skills/sf.meditation.json`                 |
| **Skill Node (`sn.*`)**   | Manifestation snapshot         | `records/skills/sn.meditation.rank1.json`           |
| **Timeline Event**        | Per-character epistemic update | `records/jake/timeline.json`                        |
| **Meta Sidecar**          | File-level provenance + audit  | `records/skills/sn.meditation.rank1.json.meta.json` |

Each layer is immutable once committed — later discoveries add *new files or new timeline events*, not edits to prior
truth.

---

## 🧠 Why This Matters

This design enables **LLMs to simulate Theory of Mind** — the ability to reason about what different entities know,
believe, and misunderstand at different times.

When trained or queried via RAG:

- The **families/nodes** provide *objective capability scaffolds* (“what this skill can do”).
- The **timelines** provide *subjective belief traces* (“what this person thinks it can do right now”).
- The **provenance system** ensures that every inference has textual grounding.

This yields generative models that can produce diegetically consistent stories with believable character knowledge
states — something current LLMs fail at because they flatten everything into omniscient narration.

---

## 🚫 Anti-Patterns (a.k.a. Don’t You Dare)

- ❌ Don’t collapse nodes together because “they’re similar.” Each manifestation is unique.
- ❌ Don’t mark older nodes or families as deprecated — nothing ever becomes obsolete.
- ❌ Don’t add new quotes to old nodes. Create new events or nodes instead.
- ❌ Don’t treat PHI like a fan wiki — it’s not about what *is true*, but about *how truth propagates through characters*.
- ❌ Don’t forget provenance — “facts without quotes” are invalid.

---

## 🧰 Next Phase Targets

1. Finalize `timeline_contract_v1.0.md` — formal rules for epistemic event logging.
2. Build validation CLI to check consistency between character belief states.
3. Prototype RAG queries:

   - “What does Jake know about Meditation by Chapter 5?”
   - “When did Amy first learn Meditation restores stamina?”
   - “Which characters misunderstand the System at this point in time?”
4. Generate derived *epistemic graphs* for training narrative LLMs.

---

## 🧠 TL;DR for Future Goldfish

If you ever catch yourself thinking *“this would be simpler if we just combined these skill versions into one file”* —
take a walk, get some coffee, and reread this document.

Simplicity is **not the goal**.
**Traceable cognition** is.

---

## 🎯 Research Problem — Why This Exists

Large Language Models can summarize stories but struggle to **recreate them faithfully** when the narrative world
depends on *who knows what, and when*. They flatten story state into omniscient narration, ignoring that each character
experiences partial, time-bound knowledge.

**Problem statement:**
Current narrative generation systems lack *diegetic epistemic modeling* — the ability to represent both objective world
state and subjective knowledge state across time.

---

## 🧠 Core Hypothesis

If story canon is encoded as a **provenance-aware, temporally indexed knowledge graph**, where every fact includes:

- its **source** (`source_ref`),
- its **time** (scene / event order),
- and its **observer** (which character knows it),

then a retrieval-augmented LLM can generate **diegetically consistent prose** that respects character knowledge limits
and world logic.

---

## 🧩 Novelty

PHI’s data model formalizes three intersecting layers rarely combined elsewhere:

1. **Diegetic layer (objective world):** what exists or happens in canon.
2. **Epistemic layer (subjective state):** who knows or believes each fact at any given time.
3. **Temporal layer (narrative order):** when those facts or beliefs were established, changed, or forgotten.

Together they create a “theory-of-mind scaffolding” for stories — a structure where characters’ beliefs, misperceptions,
and gradual learning are first-class data entities.

No current public system unites these layers within a provenance contract.

---

## 🏗️ Implementation Architecture (Current Phase)

- **Data Representation:**
Canonical records (`records/skills/`, `records/classes/`, etc.) encode world facts with `source_ref` provenance and
`record_log` audit trails.

- **Epistemic State:**
Character timelines log what each entity *learns, infers, or misremembers*, allowing reconstruction of their mental
model at any scene.

- **Validation Layer:**
Tools (`validate_provenance.py`, `validate_timeline.py`) enforce consistency between narrative evidence and database
state.

- **Derivation Layer (planned):**
An offline process will distill objective skill/fact graphs into *character-specific snapshots*, suitable for RAG or
fine-tuning contexts.

---

## 🧪 Validation Hypothesis — What We’re Testing

We will evaluate whether LLMs grounded in this data structure:

1. Produce prose that maintains **character-limited knowledge** (no omniscient leaks).
2. Exhibit **consistent world logic** across flashbacks and parallel arcs.
3. Adapt **skill behavior** in new contexts while remaining canon-faithful.

If successful, PHI will demonstrate that **structured epistemic provenance** can teach models emergent narrative
reasoning — a step toward true diegetic understanding.

---

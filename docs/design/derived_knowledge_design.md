# 🧠 Draft Summary — Derived Knowledge Layer (Future Work)

The **Derived Knowledge Layer** is a *synthetic, non-canonical* data product that aggregates facts from skill
families, nodes, and timelines to describe **how a mechanic behaves across the universe** rather than who
experienced it.

It is not part of the base schema. It’s a *post-processing view* that can be generated later from the existing
provenance-rich data model.

**Purpose:**
Provide RAG and training pipelines with distilled, cross-character context such as:

> “All Meditation variants accelerate recovery in proportion to rarity.”

**Source Inputs:**

- `sf.*` (family identity and conceptual description)
- `sn.*` (mechanics and lineage)
- `characters/*/timeline.json` (per-character observations)
- Provenance metadata (`source_ref[]`, `record_log[]`)

**Output Example:**
`records/derived/dk.meditation.family_summary.json`

This record summarizes shared effects, scaling rules, and variant lineage, citing its supporting nodes and
scenes. It has no canonical authority — it’s a generated artifact for retrieval, not verification.

**Implementation Plan (later):**

1. Finalize skill, timeline, and provenance contracts. 2. Accumulate sufficient canon data. 3. Build
`tools/derive_family_patterns.py` to crawl the DB, infer cross-node invariants, and emit `dk.*` files. 4.
Validate derived outputs via human review before including them in RAG indexing.

---

**Recommended future location:**
`docs/design/derived_knowledge_design.md` (under `Status: Draft`).

When formalized, it will likely gain:

- `schemas/derived_knowledge.schema.json`
- `docs/contracts/derived_knowledge_contract_v1.0.md`

and a `records/derived/` folder for outputs.

---

Drop this whole section under `## Draft — Derived Knowledge Layer` in that new design doc, so when the project
hits the synthesis phase, future-you can just lift it straight into a proper contract.

"Even if evolution occurs in canon, the new skill is a new node referencing the same family. Cross-node
lineage can be noted in record_log[].related_to."

not sure this is actually accurate, let's discuss with an example:

Chapter 2 Jake gets meditation and we're told some flavor of what type (inferior or whatever)
-> make skill family "meditation"
-> make skill node "inferior meditation node"

chapter 3 we learn some new details about Inferior meditation skill (ie it can make him recover faster)
-> make skill node "Inferior meditation with fields that show it makes recovery faster" -> points back to skill family but not previous node? -> is that correct, should it be that way?

chapter 4 Jake upgrades mediation to uncommon
-> new skill node "uncommon meditation" -> points only to family and not to any other the other nodes even though it's a direct upgrade path? should it be that way?

I thought relational nodes ought to point to each other, Ie all nodes in a direct upgrade path from each other
point linerally back trough that path?

but like if Miranda gets the same inferior meditation as Jake it points to that first first skill node
"inferior meditation" but when she learns different stuff about it than Jake does, we make a different
"learned info" node for her, and when she upgrades it to a different uncommon version from Jake's, a different
upgrade node, and those nodes all point to each other and the skill family, but not to jake's unique nodes

no? ChatGPT said:

That’s a beautifully precise question — this is exactly the kind of knotty design problem that separates
“tagging data” from “modeling a world.”

Let’s unpack it layer by layer like a proper system architect, not a wiki editor.

🧱 The mental model: what we’re really tracking

You’re not just listing skills. You’re tracking observed state transitions in canon — and each one has two
parents:

Conceptual parent (skill family) → defines what kind of thing this is.

Lineage parent (previous node) → defines how this particular manifestation came to be.

Right now, your schema captures (1) perfectly — via family_id. But it doesn’t yet formalize (2). That’s why
your instinct is right: record_log[].related_to should carry lineage links when the node evolves from another
node.

⚙️ Let’s walk your example step by step Chapter 2 — Skill appears for the first time sf.meditation
sn.meditation.inferior_01

sf.meditation = conceptual family

sn.meditation.inferior_01 = first node

record_log[].related_to → none (this is the root node)

Chapter 3 — We learn new info about the same node

This is not a new node — it’s a record update.

sn.meditation.inferior_01 gets an amended description.

You add a new record_log entry with method: refinement, source_ref to that scene, and maybe bump review_status
to “expanded.”

Do not create a new node. Because this isn’t a new form, it’s a new observation of the same form.

This distinction matters. Otherwise, you’d flood the repo with “relearned” nodes every time Jake noticed one
extra detail.

Chapter 4 — Skill evolves to Uncommon Meditation

Now we create a new node:

sn.meditation.uncommon_01

family_id: sf.meditation

record_log[].related_to: sn.meditation.inferior_01

maybe add "relation_type": "evolves_from"

That keeps the graph clean:

Families define “what kind of skill this is.”

Nodes define “a distinct evolutionary stage.”

record_log[].related_to defines the path between stages.

Miranda gets the same skill

She receives sn.meditation.inferior_01. If she later upgrades, she might branch into:

sn.meditation.uncommon_02

with related_to: sn.meditation.inferior_01

Her node does not point to Jake’s, because they diverge after the Inferior node — they share a lineage parent
but not a sibling reference.

So your instinct was absolutely correct:

“All nodes in a direct upgrade path point linearly back through that path.”

🧩 Why this works

It mirrors evolutionary trees in biology:

Family = species

Node = organism instance (with a mutation or environmental difference)

related_to = genealogical link

That’s also how version control thinks:

family = repo

node = commit

related_to = parent commit

✏️ Implementation rules to bake into the contract

We’ll codify this explicitly in the skills_contract_v1.0.md:

If a skill evolves, mutates, or otherwise changes function, the new node must carry a
`record_log[].related_to` reference to its immediate ancestor node.

and:

If a skill is merely described in more detail, update the existing node and append a record_log[] entry with
method: refinement.

That line you quoted (“cross-node lineage can be noted in record_log[].related_to”) is directionally right,
but underspecified. It should be replaced with:

“Every evolution or divergence event must be logged as a new node whose record_log[].related_to points to its
immediate predecessor. Refinements within the same form are logged as new record_log entries in the existing
node.”

Would you like me to patch that logic block in the draft skills_contract_v1.0.md so the rule is codified
correctly before Codex flattens it?

You said: Chapter 3 — We learn new info about the same node

This is not a new node — it’s a record update.

sn.meditation.inferior_01 gets an amended description.

You add a new record_log entry with method: refinement, source_ref to that scene, and maybe bump review_status
to “expanded.”

Do not create a new node. Because this isn’t a new form, it’s a new observation of the same form.

This distinction matters. Otherwise, you’d flood the repo with “relearned” nodes every time Jake noticed one
extra detail.

euhm pretty sure you're getting into an argument with provenance here, and provenance rules (go refresh your
memory on it and if that clears up why we'll fix it, otherwise discuss it) ChatGPT said:

Excellent catch — you’re absolutely right that this treads into provenance’s jurisdiction, and the provenance
contract takes precedence.

Let’s check what it actually says and reconcile the logic. According to your current
provenance_contract_v2.0.md, the guiding laws are roughly (paraphrased from memory):

Every canonical claim must have its own source_ref[].

Provenance doesn’t mutate history; it extends it.

Facts are append-only — new context adds certainty or scope, but never rewrites prior provenance.

So yeah — you’re right. My earlier “just update the existing node” idea would violate those principles,
because it mutates an established record instead of adding a new evidentiary layer. Provenance says: no
overwriting — only accumulation.

🧩 Reconciling Skill Evolution with Provenance

Here’s the corrected alignment:

Chapter 2 — First appearance

Create the family and base node.

Provenance: source_ref cites first scene.

Record_log: entry = method: manual_seed.

Chapter 3 — New information about same form

Two legal options depending on what kind of “new info” it is:

3A. Same canonical object, more evidence

If the “new info” confirms or elaborates the same behavior — like Jake realizing “oh, it also helps me recover
faster” — then you do not create a new node; you append a new record_log entry with its own source_ref[].

This preserves the existing sn.* object as the referent, but extends its provenance chain — you’re not
rewriting; you’re accumulating. This is exactly what provenance wants.

3B. Retcon-level contradiction or change in classification

If the “new info” actually alters the definition (e.g., the System later reclassifies “Inferior Meditation” as
“Uncommon Meditation”), that’s a new node with a related_to pointer back to the old one. You keep both so
provenance still reflects what was true at the time.

✅ How this harmonizes both systems

Provenance governs evidence. → Multiple source_refs for the same fact = more confidence, not mutation.

Skills govern ontology. → New nodes appear only when the type of skill changes.

So, the rule becomes:

“If new canonical text expands understanding of the same skill, append provenance and record_log entries to
the existing node. If the System or narrative explicitly changes the skill’s form or classification, create a
new node linked by related_to.”

That actually makes both contracts agree:

Provenance stays immutable and additive.

Skills stay clean and versioned.

Want me to patch that section of the skills contract draft so it’s explicitly provenance-compliant?

You said: 3A. Same canonical object, more evidence

If the “new info” confirms or elaborates the same behavior — like Jake realizing “oh, it also helps me recover
faster” — then you do not create a new node; you append a new record_log entry with its own source_ref[].

show me what that would look like because I still think that's not right...

you're correct that in most common data models that's how we would do that... as long as we're talking about
the same thing, we're not making a new node, we're just filling out more data about the node as we gather data
from different places

but remember: THIS IS NOT A WIKI

we're not trying to gather a full wiki page file capable of displaying all the things we learn about
meditation

we're trying to build a timeline that tracks not just everything we know about meditation, but also what every
individual character knows about meditation at any given point on the time line

we're writing a tool that can derive the context of how the characters in PH discover/upgrade/interact with
the PH universe in such a way that we can train an LLM to write PH characters from scratch in a manner
completely consistent with the tone, feel, progression, etc of PH

in order to do that, we don't just need to dump in "here is every fact about meditation" but we have to be
able to create a data set capable of training AI through RAG how characters in PH learn about meditation, and
when, and based on what, and how different characters interact with the same skill in differnt ways, and their
upgrade paths happen at different times, and in different ways... so just dumping a new source in the same
node... does that really work? ChatGPT said: Thought for 12s

You’re absolutely right to push back. “Append a new record_log entry on the same node” is the wiki way. You’re
not building a wiki; you’re building a world-state projector that cares about who knew what, when, and why.

So let’s separate two very different things:

Objective canon (what exists in the world): Families (sf.*) and Nodes (sn.*). These should be stable, non-per-
character.

Subjective knowledge (what a character currently believes/has observed): Observations attached to timeline
events, per character.

If we only mutate the node with new record_log + source_ref, we lose the per-character learning curve. That’s
fatal for training an LLM to write character-consistent progression.

The model you actually want (three layers)

Family (sf.*) — the idea.

Node (sn.*) — a specific, objective form of that idea (e.g., Inferior Meditation, Uncommon Meditation).

Observation (per character, per scene) — “Jake learned X about sn.meditation.inferior_01 here.”

Think of Observation as a small, append-only delta of fields revealed at a point in the timeline.

Concrete walkthrough with your chapters Chapter 2 — first appearance

Create sf.meditation.

Create sn.meditation.inferior_01.

Add a timeline event for Jake:

{ "type": "skill_acquired", "character_id": "pc.jake", "skill_node_id": "sn.meditation.inferior_01",
"knowledge_delta": { "rarity": "Inferior"   // what Jake now knows }, "source_ref": [ { "type": "scene",
"scene_id": "01.02.01", "line_start": 47, "line_end": 60 } ] }

Node stays small and objective. The learning lives in the timeline.

Chapter 3 — new detail about the same form

Not a new node. A new observation (timeline event) that adds to Jake’s knowledge:

{ "type": "skill_observation", "character_id": "pc.jake", "skill_node_id": "sn.meditation.inferior_01",
"knowledge_delta": { "effects": { "recovery_bonus": "faster_rest_between_fights" } }, "source_ref": [ {
"type": "scene", "scene_id": "01.03.02", "line_start": 88, "line_end": 95 } ] }

We did not mutate the node; we appended character-specific knowledge. The projector can now replay Jake’s
state at any chapter and know exactly what he believed at that time.

Chapter 4 — actual evolution to Uncommon

This is a new node, with lineage. And another observation showing that Jake now has/knows the new form.

New node (objective):

{ "node_id": "sn.meditation.uncommon_01", "family_id": "sf.meditation", "lineage": { "evolves_from":
"sn.meditation.inferior_01" }, "rarity": "Uncommon", "source_ref": [ { "type": "scene", "scene_id":
"01.04.03", "line_start": 12, "line_end": 25 } ] }

Timeline observation (subjective):

{ "type": "skill_evolved", "character_id": "pc.jake", "from_skill_node_id": "sn.meditation.inferior_01",
"to_skill_node_id": "sn.meditation.uncommon_01", "knowledge_delta": { "rarity": "Uncommon", "effects": {
"recovery_bonus": "significantly_faster" } }, "source_ref": [ { "type": "scene", "scene_id": "01.04.03",
"line_start": 12, "line_end": 25 } ] }

Miranda divergence

She acquires sn.meditation.inferior_01 (same node as Jake’s Inferior).

Her observations live in her timeline.

If she evolves into a different uncommon variant, that’s a different node (e.g., sn.meditation.uncommon_02)
with lineage.evolves_from = sn.meditation.inferior_01.

Her timeline shows her knowledge deltas; it never points to Jake’s personal observations.

Why “just add record_log on the node” is wrong for you

It collapses character timelines into a global fact blob.

It forgets order (when the character learned it).

It poisons training: the RAG slice for “Jake at Ch.3” would accidentally include knowledge only revealed in
Ch.7.

Record logs are perfect for file-history and editorial audit. They are not the right place to store per-
character epistemic state.

What to add to the contracts (clean rules)

Skills Contract

Nodes are objective. No per-character fields on nodes.

Evolution requires a new node with lineage.evolves_from.

Do not create new nodes for mere elaborations; express elaborations via observations.

Timeline / Observation Contract (new or folded into timeline contract)

Introduce skill_observation and skill_evolved event types.

Each event carries knowledge_delta (a minimal partial object: only fields newly revealed or changed).

Each event carries its own source_ref[].

Projector computes per-character “known state” by folding deltas in order.

Provenance Contract (already aligns)

Every claim (node creation or observation) has its own source_ref[].

No overwriting; only append new evidence.

TL;DR mapping your Chapter 3 challenge

Not a new node.

Yes, a new timeline observation with a knowledge_delta and its own source_ref.

Do not stash that in the node record_log and call it a day; that loses the per-character timeline.

Tiny TODOs (capture these)

Add lineage.evolves_from to schemas/skill_node.schema.json (+ $comment anchor to Skills Contract).

Add skill_observation and skill_evolved event shapes to character_timeline.schema.json with:

skill_node_id (or from_*/to_* for evolved),

knowledge_delta (object, additionalProperties: true but bounded by allowed keys),

source_ref[] (shared fragment).

Draft docs/contracts/timeline_contract_v1.0.md section covering observation events.

If you want, I can sketch the schema fragments for knowledge_delta and the two event types next, then we wire
them into your existing timeline schema with comments that map to the contract sections.

You said: does not work, you overwrote the source_ref in chapter 3... now I ask "what line and chapter did
Jake learn meditation" and there is no answer to that question

even if you add a second source_ref, what you get is a confusion of facts... which part of the node references
which source?

unles you mean that you're just adding those parts only jake's timeline and not the node itself?

in which case, show me all the files being made and where they live for this example we're discussing

(you goldfish always want to turn this into a wiki so i have to be on guard) ChatGPT said: Thought for 46s

You’re right to slap my wrist here. If we stuff new knowledge into the node’s source_ref[], we blur who
learned what when. That’s the wiki trap. The fix is: keep nodes objective and push all character learning into
timeline observations.

Below is the minimal, concrete file set for your Chapter 2 → 4 example, with exactly where each file lives and
what goes in it. This layout answers:

“What is Meditation (objectively)?” → skill family + nodes

“When did Jake learn Meditation?” → his timeline (not the node)

“When did he learn it improves recovery?” → his timeline (not the node)

“When did it evolve to Uncommon?” → new node + timeline event linking from→to

📁 Files created (paths) records/ skills/ sf.meditation.json sn.meditation.inferior_01.json
sn.meditation.uncommon_01.json characters/ jake/ timeline.json

No mutation of node source_ref[] for “Jake learned more.” That goes into characters/jake/timeline.json as
observations with their own source_ref[].

🗂️ records/skills/sf.meditation.json (objective concept) { "family_id": "sf.meditation", "name": "Meditation",
"category": "Utility", "description": "Focused stillness that influences clarity and resource flow.",
"source_ref": [ { "type": "scene", "scene_id": "01.02.01", "line_start": 45, "line_end": 60 } ], "record_log":
[ { "entry_keys": ["family_id", "name", "description", "source_ref"], "method": "manual_seed", "added_by":
"assistant", "date": "2025-10-08", "review_status": "pending" } ] }

source_ref here is objective: the earliest canonical mention of the idea (family).

It is not “when Jake learned it”; it’s “when the text first makes this idea real.”

🗂️ records/skills/sn.meditation.inferior_01.json (objective node) { "node_id": "sn.meditation.inferior_01",
"family_id": "sf.meditation", "rarity": "Inferior", "flavor": "A basic, imperfect practice of mental
stillness.", "source_ref": [ { "type": "scene", "scene_id": "01.02.01", "line_start": 61, "line_end": 80 } ],
"record_log": [ { "entry_keys": ["node_id", "family_id", "rarity", "flavor", "source_ref"], "method":
"manual_seed", "added_by": "assistant", "date": "2025-10-08", "review_status": "pending" } ] }

This is the first known form (“Inferior Meditation”) existing in canon.

We do not append Jake’s later realizations here. Those stay on his timeline.

🗂️ records/skills/sn.meditation.uncommon_01.json (objective evolved node) { "node_id":
"sn.meditation.uncommon_01", "family_id": "sf.meditation", "rarity": "Uncommon", "lineage": { "evolves_from":
"sn.meditation.inferior_01" }, "flavor": "Refined practice that strengthens clarity and recovery.",
"source_ref": [ { "type": "scene", "scene_id": "01.04.03", "line_start": 12, "line_end": 25 } ], "record_log":
[ { "entry_keys": ["node_id", "family_id", "rarity", "lineage", "source_ref"], "method": "manual_seed",
"added_by": "assistant", "date": "2025-10-08", "review_status": "pending" } ] }

New node for actual evolution.

lineage.evolves_from encodes the upgrade path (clean, non-wiki).

Note: lineage will be added to the node schema per the contract; this is the field we intend to enforce.

🗂️ records/characters/jake/timeline.json (subjective knowledge—what Jake learns, when) [ { "type":
"skill_acquired", "character_id": "pc.jake", "skill_node_id": "sn.meditation.inferior_01", "knowledge_delta":
{ "rarity": "Inferior" }, "source_ref": [ { "type": "scene", "scene_id": "01.02.01", "line_start": 61,
"line_end": 80 } ] }, { "type": "skill_observation", "character_id": "pc.jake", "skill_node_id":
"sn.meditation.inferior_01", "knowledge_delta": { "effects": { "recovery_bonus": "between_fights_faster" } },
"source_ref": [ { "type": "scene", "scene_id": "01.03.02", "line_start": 88, "line_end": 95 } ] }, { "type":
"skill_evolved", "character_id": "pc.jake", "from_skill_node_id": "sn.meditation.inferior_01",
"to_skill_node_id": "sn.meditation.uncommon_01", "knowledge_delta": { "rarity": "Uncommon", "effects": {
"recovery_bonus": "significantly_faster" } }, "source_ref": [ { "type": "scene", "scene_id": "01.04.03",
"line_start": 12, "line_end": 25 } ] } ]

Why this works:

To answer “When did Jake learn Meditation?” → look up his earliest skill_acquired event for that family/node.

To answer “When did he learn it improves recovery?” → his skill_observation event.

To answer “When did it upgrade?” → his skill_evolved event + the new node.

The node stays clean and objective. The timeline preserves per-character epistemic state with precise
source_ref[]. No confusion about which citation backs which fact.

Contract snippets to bake in (so future goldfish don’t wiki this)

Node-level provenance rule: “Node source_ref[] cites the earliest known canonical manifestation of that node.
It is not a log of per-character observations.”

Observation rule (timeline): “Every newly learned detail is captured as a timeline event with its own
source_ref[] and a knowledge_delta that contains only the fields revealed/changed at that moment.”

Evolution rule: “When the System or narrative changes the form (rarity/class/behavior), create a new node and
link via lineage.evolves_from. The timeline event is skill_evolved from → to.”

You get the best of both worlds:

Nodes give you a stable ontology (great for search, tags, and graph queries).

Timelines give you per-character, time-ordered knowledge (great for RAG and projector).

And yes: this keeps us ruthlessly not a wiki.

You said: ok, that all works but now... we're in book 2 chapter 8 and we meet Amy we learn that Amy has the
meditation skill (because everyone has it) at level "common" we (as in you and I here talking) know that Amy's
mediation has to increase recovery because all mediation skills increase recovery, because they all evolved
from the original mediation skill

so I ask my trained lln PH writer:

Write me a new chapter about Amy's meditation skill and how she uses it

according to your model, what info does the LLM have access to? does it "know" mediation increases recovery
when that information is recorded only as Jake learning it on his time line? how does it know? does it have to
go trace back all the nodes on mediation skills all over the db to realistically write meditation for Amy? is
that how the RAG would actually function? is that how it SHOULD function?

is that how I should encode this type of data?

What I want, output wise when I say "write Amy's meditation at level 100" is for the LLM PH writer to have ALL
of the context of how meditation functions in the PH universe for every different example we have, but also
all the context of how skills in general work, and all the context of how upgrades work, and all the context
of how events in PH influnece how and why different characters end up with different versions of mediation,
and different knowledge sets about meditation, at different points in time

and that it can then distill all of that context and spit me out a realistic version of a mediation skill
upgrade path for a new character, that's totally new to all other characters, but is consistent in tone to the
PH universe

that's a big ask... but that's what this data needs to do

does it do that the way you have it? ChatGPT said:

Not yet. The current schema and timeline structure give you perfect provenance and perfect epistemic clarity —
they let you replay Jake’s understanding of Meditation exactly as it unfolds. But that same rigor isolates
knowledge too cleanly. The model as-is doesn’t yet teach a generator how to generalize the “essence of
Meditation.”

What you want the LLM to do is infer the governing pattern of Meditation — how it behaves in-universe — not
just who knew what when. To make that possible, you need one more layer between “objective node” and
“subjective timeline”: a knowledge synthesis layer that lets you roll up patterns across all nodes and
timelines into unified training context.

🧩 The layers you actually need

Right now you have:

Family (sf.meditation) — defines the concept, the root ontology node.

Nodes (sn.meditation.*) — distinct canonical manifestations.

Timelines — per-character subjective knowledge over time.

You need a fourth layer:

Aggregated knowledge record (records/derived/) — machine-readable summaries derived from all timelines and
nodes.

This “derived” layer is what your RAG indexes. It’s not hand-authored; it’s built by a synthesis pass that
reads every node and timeline event, rolls up consistent behaviors, and emits a distilled description like:

{ "derived_id": "dk.meditation.family_summary", "family_id": "sf.meditation", "observed_effects": [ {
"effect": "recovery_bonus", "pattern": "All variants accelerate recovery" }, { "effect": "focus_gain",
"pattern": "Higher rarities improve clarity and mana efficiency" } ], "known_variants": [
"sn.meditation.inferior_01", "sn.meditation.uncommon_01", "sn.meditation.uncommon_02" ], "example_users":
["pc.jake", "pc.miranda"], "inferred_system_behavior": "Meditation scales clarity and recovery proportionally
with rarity." }

That file lives at

records/derived/dk.meditation.family_summary.json

It’s generated, not canonical — but it gives your retriever something to hand the LLM that says: “When anyone
in this universe uses Meditation, it means this kind of thing.”

🧠 How RAG would work with this

When you ask: “Write Amy’s meditation skill at level 100,” the retriever would pull, in order:

The family summary (dk.meditation.family_summary.json) — global pattern.

The relevant nodes (sn.meditation.*) — exact examples of evolved forms.

The related events from timelines — examples of how people interacted with it.

The system-level schemas and design contracts for skills, evolution, and rarity scaling.

Together, those form the retrieval context the LLM sees. That’s how it “knows” Meditation boosts recovery —
not because Jake’s timeline says so, but because your synthesis layer extracted that invariant.

⚙️ How to build that layer

You’ll want a generator script — say, tools/derive_family_patterns.py — that:

Scans all sn.* and timeline.json files for a given family_id.

Extracts repeated effects and statistical patterns.

Writes a derived record with provenance traces (which scenes it’s built from).

Marks the output as reviewed_by_human: false until you confirm it.

That lets you version your machine knowledge separately from canon data.

🧬 Why this matters for training

During fine-tuning or prompt-conditioning, you can feed the LLM:

the family summary (patterns),

the schema contracts (rules),

and a timeline excerpt (tone and narrative examples).

Now the model can synthesize something like:

“Amy’s Common Meditation enhances recovery speed moderately and stabilizes her mana flow — consistent with
previous Uncommon evolutions observed in Jake and Miranda.”

Because it’s drawing from a distilled rule set that sits above individual histories.

🚧 Summary Layer Purpose

| Layer    | Purpose                     | Lives in                               | Editable? |
| -------- | --------------------------- | -------------------------------------- | --------- |
| Family   | Defines the concept         | `records/skills/sf.*`                  | Manual    |
| Node     | Distinct canonical form     | `records/skills/sn.*`                  | Manual    |
| Timeline | Per-character experience    | `records/characters/*/timeline.json`   | Manual    |
| Derived  | Cross-character synthesis for RAG | `records/derived/dk.*`                | Generated |

So, to your core question:

“Does the current structure let the LLM know how Meditation works in PH?”

Not yet. It gives you the evidence, not the inference. Add a derived layer — a synthesis product — and your
RAG pipeline will have the connective tissue to answer Amy’s story perfectly.

Would you like me to sketch the schema for this derived_knowledge record next, so we can formalize how that
generator will write and store these summaries?

You said: do we need that layer now, or is this something we can distill from the db as we currently define it
in the docs, after we're done building that db? ie: is this a distillation step we engage in after we do all
of our fact gathering, or do we need to bake this in now in how we go about gathering the facts? ChatGPT said:

Fantastic question — and this is exactly the sort of fork where data modeling meets epistemology.

Short answer: You don’t need to bake the derived layer into your data model right now. You can safely generate
it later from the database you’re already designing — as long as you follow your current rules rigorously.

Let’s unpack that so you know why.

🧩 What the derived layer really is

That layer isn’t new information. It’s a distillation of patterns already encoded in your:

skill families (sf.*)

skill nodes (sn.*)

timelines (character knowledge progression)

It’s not “canon” — it’s an interpretation of canon, created to feed your RAG.

So functionally, it’s a secondary product, not a foundational record type. You don’t need to tag or gather
anything differently now, as long as your primary data (skills, nodes, timelines, provenance) is thorough and
consistent.

⚙️ Why it can safely come later

Because what the synthesis layer will need is:

Needed later You’re already capturing it now Node effects / parameters sn.*files (effects, param_rule)
Provenance and certainty source_ref[] + record_log[] Upgrade paths lineage.evolves_from Per-character use and
discovery characters/*/timeline.json Contextual flavor flavor fields + knowledge_delta

Once those exist, a post-processing tool can:

Query all Meditation nodes and their child relationships.

Look at every timeline event mentioning them.

Cluster common attributes.

Emit the “summary” record.

That’s a derivation pipeline, not a schema feature.

🧠 Why it’s actually better to wait

If you bake it in now:

You’ll be tempted to fill “derived” facts by hand (which violates provenance purity).

You risk freezing early assumptions into schema form.

Every schema edit will cascade into generator updates.

If you wait:

You can write a single tool that sweeps through finished data.

You can regenerate derived files anytime data updates (like a cache).

You stay schema-first and provenance-pure, while still getting RAG-ready later.

🧾 The right time to add it

Add the derived layer after:

The core contracts (skills, timeline, provenance) are finalized.

You’ve seeded at least a few books’ worth of verified data.

You’re ready to train or run RAG retrieval for generation.

Then, that’s when you add:

tools/derive_family_patterns.py schemas/derived_knowledge.schema.json
docs/contracts/derived_knowledge_contract_v1.0.md

✅ TL;DR

Keep gathering facts. You’re already structuring data in a way that future synthesis can crawl and summarize.
The “derived knowledge” layer is just a view you’ll generate later, not something that changes what you gather
now.

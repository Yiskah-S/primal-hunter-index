# 📜 PHI Provenance & ID Contract (v1)

**Updated:** 2025-10-05

All referencable entries must carry a stable ID

Format: type.segment.segment, lowercase snake_case

Example: tag.skills.teleportation

Regex: ^(sn|sf|eq|cl|rc|pc|loc|tag|ev)\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$

---

## TL;DR

- Everything that can be referenced gets a stable ID (human‑readable).
- Canon files in `records/` stay lightweight facts.
- All the rich context (who/when/why/where/how sure) lives in sidecars and timelines.
- Tags follow a shared schema and must exist in the tag registry (or be explicitly approved).
- Provenance uses `source_ref[]` with scene/line spans (and optional quotes). Multiple spans allowed.
- Nothing breaks if names change, because links are by ID, not by label.

---

## 0) Design Goals

- **Referential solidity**: facts, events, tags, reviews, and quotes all point at stable IDs.
- **Small canon, rich context**: the payload you RAG over is clean; deep metadata stays out of band.
- **Append-only history**: you can layer new knowledge without rewriting the past.
- **Toolable**: validators, CLIs, and editors can follow one consistent contract.

---

## 1) IDs — The Backbone

### 1.1 ID Format

- Style: `lower_snake` segments joined by dots, with a short type prefix.

#### Prefixes:

| Prefix | Entity type     | Example                      |
|--------|------------------|------------------------------|
| `sf.`  | Skill Family      | `sf.meditation`              |
| `sn.`  | Skill Node        | `sn.meditation.rank1`        |
| `eq.`  | Equipment         | `eq.cloak_of_phasing`        |
| `cl.`  | Class             | `cl.void_warden`             |
| `rc.`  | Race              | `rc.dryad`                   |
| `pc.`  | Character         | `pc.jake`                    |
| `loc.` | Location          | `loc.haven_city`             |
| `tag.` | Tag (internal)    | `tag.skills.teleportation`   |
| `ev.`  | Event (optional)  | `ev.jake.01_02_01.a`         |

> Stability: IDs don’t change. If something evolves, create a new ID and link them.

---

### 1.2 Core Invariants

- Every referencable object MUST have `id` and a single source-of-truth file.
- All cross-file references MUST use `id`, not labels/names.

---

## 2) File Layers & Responsibilities

### 2.1 Canon Payloads (`records/*.json`)

- Contains: minimal, quote-free facts + optional `tags`
- Must include: `id` (and `family_id` when relevant)

```json
{
  "id": "sn.spectral_displacement.rank1",
  "family_id": "sf.spectral_displacement",
  "rarity": "epic",
  "type": "combat_utility",
  "description": "Phase out of the physical world for a split instant, displacing your position.",
  "effects": {
    "duration_s": 0.5,
    "cooldown_s": 10,
    "movement_type": "teleport"
  },
  "tags": {
    "skills": ["teleportation", "spectral"],
    "affinity": ["void"],
    "combat_role": ["assassin"]
  }
}
````

---

### 2.2 Sidecars (e.g. `.meta.json`, `.review.json`, `.provenance.json`)

* `.meta.json` — audit log + local provenance + inference weights
* `.review.json` — reviewer actions, warnings, QA info
* `.provenance.json` — optional inverse map from scenes → IDs

Example `.meta.json`:

```json
{
  "sn.spectral_displacement.rank1": {
    "index_meta": {
      "added_by": "assistant",
      "added_on": "2025-10-08",
      "method": "promote_tags",
      "reviewed_by": "user",
      "review_status": "approved"
    },
    "record_log": [
      { "action": "added", "by": "assistant", "date": "2025-10-08" },
      { "action": "approved", "by": "user", "date": "2025-10-08" }
    ],
    "source_ref": [
      {
        "type": "scene",
        "scene_id": "03-14-01",
        "line_start": 212,
        "line_end": 225,
        "quote": "Jake vanished mid-dash, flickering back into reality a meter behind the specter."
      }
    ],
    "links": [
      { "type": "upgrades_to", "target": "sn.spectral_displacement.rank2" },
      { "type": "granted_by", "target": "eq.cloak_of_phasing" }
    ]
  }
}
```

---

### 2.3 Timelines (`records/characters/*/timeline.json`)

* Events always reference `id`s (e.g. `node_id`, `eq_id`)
* Each event can carry its own `tags`, `source_ref`, and metadata

---

## 3) `source_ref` Contract

### 3.1 Format

```json
{
  "type": "scene|wiki|user|inferred|external",
  "scene_id": "01-02-03",
  "line_start": 111,
  "line_end": 120,
  "quote": "optional snippet"
}
```

* Always prefer quote-backed references
* `type: inferred` must only appear if schema/registry explicitly allows it

---

## 4) Tags — Schema & Registry

### 4.1 Shared Schema

Used anywhere a `tags` block appears:

```json
{
  "type": "object",
  "patternProperties": {
    "^[a-z_]+$": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9_]+$" }
    }
  }
}
```

---

### 4.2 Tag Registry

Example:

```json
{
  "skills": [
    {
      "tag": "teleportation",
      "status": "approved",
      "allow_inferred": false,
      "aliases": ["blink"]
    }
  ]
}
```

* Only tags in the registry may be used
* `allow_inferred = false` → quote required

---

## 5) Links (graph-style relations)

Lives in `.meta.json`:

```json
"links": [
  { "type": "upgrades_to", "target": "sn.meditation.rank2" },
  { "type": "granted_by", "target": "eq.cloak_of_phasing" }
]
```

---

## 6) Validation Rules

* All IDs must follow `type.segment.segment` pattern
* No inline provenance in canon (except for timelines)
* Sidecars must validate against their own schemas

---

## 7) Sample Workflows

* Add a skill → `sf.*` + `sn.*` + `.meta.json` + `timeline.json` (optional)
* Update a skill → add `timeline` entry + amend `.meta.json`
* Upgrade path → create new `sn.*` and link via `.meta.json`
* Promote a tag → update `tag_registry.json` + tag’s `.meta.json`

---

## 8) Policy Tips

* Don’t rename IDs (ever)
* Use `record_log[]` to track change history
* Use `.provenance.json` only when necessary (inverse mapping or quote reuse)

---

## 9) Glossary

* **Canon** — the clean, lean file in `records/`
* **Sidecar** — `.meta.json`, `.review.json`, etc.
* **Registry** — authoritative list (e.g., tags)
* **source_ref** — where a fact was observed
* **ID** — stable string, used as a pointer

---

## 10) Appendix: Micro-Schemas

### source_ref.schema.json

```json
{
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": { "enum": ["scene", "wiki", "user", "inferred", "external"] },
    "scene_id": { "type": "string", "pattern": "^\\d{2}-\\d{2}-\\d{2}$" },
    "line_start": { "type": "integer", "minimum": 1 },
    "line_end": { "type": "integer", "minimum": 1 },
    "quote": { "type": "string", "maxLength": 400 }
  },
  "allOf": [
    {
      "if": { "properties": { "type": { "const": "scene" } } },
      "then": { "required": ["scene_id", "line_start", "line_end"] }
    }
  ]
}

















## 🛠️ Just a few *tiny* things to lock in

### 1. **ID Contract** — needs a pinned regex + enforcement

You describe ID prefixes well (`sn.`, `sf.`, etc.), but your contract will be even stronger with:

```jsonc
"pattern": "^(sn|sf|eq|cl|rc|pc|loc|tag|ev)\\.[a-z0-9_]+(\\.[a-z0-9_]+)*$"
```

Or just document this explicitly in a `docs/provenance_contract.md → ID Contract` section.

Then codify:

* **Required:** all cross-file references use `id`, never label
* **Immutable:** once assigned, an ID never changes — only links

This gives you bulletproof schema-based enforcement and future-proof cross-indexing.

---

### 2. **Make `record_log[]` required** in `.meta.json`

You already include it — great — but make it **mandatory** in the schema now.

It enables:

* Diffing and blame tracking
* Change explanations (“why did we promote this skill to canon?”)
* Replay-based debugging

---

### 3. **Add `type` field to `source_ref` now**

You already planned this (`scene|wiki|user|external|inferred`) — now bake it into:

* Shared `source_ref.schema.json`
* Every `source_ref[]` entry (timeline, .meta.json, etc.)

Why now?

* Makes wiki-based scraping easier later
* Gives you a bridge to community-tagged data
* Avoids retrofitting mess later

---

### 4. **Justify per-tag use (optional)**

Your tag schema is great. To go **next-level**:

Add an optional field on events or scenes:

```json
"tags_justification": {
  "spectral": "teleport effect described as phasing out",
  "ambush": "attacked from behind"
}
```

That gives LLM auditability and human reviewers more confidence.

You can store this in timeline events or `.review.json` (up to you).

---

### 5. **Bundle migration (optional for later)**

You're storing each canon entry as:

```
records/skills.json → one giant dict
schemas/...
```

Eventually, for “thicc” entries, migrate to:

```
records/skills/sn.spectral_displacement.rank1/
├── record.json
├── meta.json
├── review.json
```

But only when an entry earns it (like a VIP room). Don’t force it on everything.

---

### 6. **Where the contract is strongest**

* The **tag registry + inferred guardrails** = top-tier control
* The **sidecar split** (meta vs review vs provenance) = scalable
* The **timeline-driven updates** = lets you simulate event sourcing without rewriting core
* The **focus on stability** = future-RAG will thank you

---

## 🧭 Optional enhancements

Not required, but may be helpful:

| Idea                             | Benefit                             | When     |
| -------------------------------- | ----------------------------------- | -------- |
| `source_ref.type` (scene, wiki…) | Future-proof + LLM-friendly         | **Now**  |
| Required `record_log[]`          | Enables change tracking + replay    | **Now**  |
| `docs/provenance_contract.md`    | One source of truth for future devs | **Now**  |
| tools/build_meta_index.py        | Fast CLI/UI access to review states | Soon     |
| tools/projector.py               | Snapshot view from timeline         | Later    |
| Justification per tag use        | Audit-friendly                      | Optional |
| Optional `tags.json` per scene   | Auto-generated, not hand-authored   | Optional |









Provenance System Contract (v1) — Phi
📜 PHI Provenance & ID Contract (v1)

Updated: 2025-10-05

TL;DR

Everything that can be referenced gets a stable ID (human‑readable).

Canon files in records/ stay lightweight facts.

All the rich context (who/when/why/where/how sure) lives in sidecars and timelines.

Tags follow a shared schema and must exist in the tag registry (or be explicitly approved).

Provenance uses source_ref[] with scene/line spans (and optional quotes). Multiple spans allowed.

Nothing breaks if names change, because links are by ID, not by label.

0) Design Goals

Referential solidity: facts, events, tags, reviews, and quotes all point at stable IDs.

Small canon, rich context: the payload you RAG over is clean; deep metadata stays out of band.

Append-only history: you can layer new knowledge without rewriting the past.

Toolable: validators, CLIs, and editors can follow one consistent contract.

1) IDs — The Backbone

Rule: If it can be referenced across files, it gets a stable id.

1.1 ID Format

Style: lower_snake segments joined by dots, with a short type prefix.

Prefixes (suggested):

sf. = skill family → sf.meditation

sn. = skill node (versioned/rank) → sn.meditation.rank1

eq. = equipment → eq.cloak_of_phasing

cl. = class → cl.void_warden

rc. = race → rc.dryad

pc. = person/character → pc.jake

loc. = location → loc.haven_city

tag. = tag key (if needed internally) → tag.skills.teleportation

ev. = timeline event (optional) → ev.jake.01_02_01.a

Stability: IDs don’t change. If something evolves, create a new ID and link them (see links below).

1.2 Core Invariants

Every referencable object MUST have id and a single source of truth file.

All cross-file references MUST use id, not labels/names.

2) File Layers & Responsibilities
2.1 Canon Payloads (records/**.json)

What goes here: minimal, quote-free facts + optional tags.

Why: smaller, faster retrieval; fewer churny diffs.

Must include: id (and family_id when relevant).

Example – skill node (canon):

{
  "id": "sn.spectral_displacement.rank1",
  "family_id": "sf.spectral_displacement",
  "rarity": "epic",
  "type": "combat_utility",
  "description": "Phase out of the physical world for a split instant, displacing your position.",
  "effects": {
    "duration_s": 0.5,
    "cooldown_s": 10,
    "movement_type": "teleport"
  },
  "tags": {
    "skills": ["teleportation", "spectral"],
    "affinity": ["void"],
    "combat_role": ["assassin"]
  }
}
2.2 Sidecars (same path + .meta.json, .review.json, .provenance.json)

.meta.json — audit + local provenance + inference weights

{
  "sn.spectral_displacement.rank1": {
    "index_meta": {
      "added_by": "assistant",
      "added_on": "2025-10-08",
      "method": "promote_tags",
      "reviewed_by": "user",
      "review_status": "approved",
      "notes": "Approved from candidate; verified Book 03"
    },
    "record_log": [
      { "action": "added", "by": "assistant", "date": "2025-10-08" },
      { "action": "approved", "by": "user", "date": "2025-10-08" }
    ],
    "source_ref": [
      {
        "type": "scene",
        "scene_id": "03-14-01",
        "line_start": 212,
        "line_end": 225,
        "quote": "Jake vanished mid-dash, flickering back into reality a meter behind the specter."
      }
    ],
    "inference": {
      "allow_inferred": false,
      "confidence": 0.98,
      "source_priority": "direct_quote",
      "importance": 0.9,
      "context_weight": 1.0
    },
    "links": [
      { "type": "upgrades_to", "target": "sn.spectral_displacement.rank2", "reason": "Observed rank-up in arc 4" },
      { "type": "granted_by", "target": "eq.cloak_of_phasing", "reason": "Item grants/displaces skill behavior" }
    ]
  }
}

.review.json — reviewer decisions, QA warnings, training vs runtime knobs

{
  "sn.spectral_displacement.rank1": {
    "decisions": [
      { "by": "user", "date": "2025-10-08", "action": "approve", "notes": "Matches quote; keep duration strict" }
    ],
    "warnings": [
      { "code": "vagueness", "message": "Effect wording differs in B03 vs B04; keep conservative." }
    ],
    "scoring": {
      "training_score": 0.85,
      "retrieval_score": 1.0,
      "bias_class": "narrative"
    }
  }
}

.provenance.json — optional inverse map / heavy context

{
  "03-14-01": {
    "contributes_to": ["sn.spectral_displacement.rank1"],
    "lines": [212, 225]
  }
}

Keep .provenance.json optional; only use when inverse lookup is needed or quotes are large.

2.3 Timelines (records/**/timeline.json)

Events reference IDs (node_id, family_id, eq_id, …).

Events carry their own source_ref[] and can include tags.

Example – character event:

{
  "event_id": "ev.jake.03_14_01.a",
  "when": "03-14-01",
  "type": "skill_used",
  "node_id": "sn.spectral_displacement.rank1",
  "observed_params": { "duration_s": 0.5 },
  "tags": { "combat_context": ["ambush", "spectral"] },
  "source_ref": [
    { "type": "scene", "scene_id": "03-14-01", "line_start": 212, "line_end": 225 }
  ]
}
3) Provenance (source_ref) Contract
3.1 Shape

A source_ref can be a single object or an array of them.

{
  "type": "scene|wiki|user|inferred|external",
  "scene_id": "BB-CC-SS",     
  "line_start": 120,
  "line_end": 132,
  "quote": "optional, short snippet (<= 280 chars)"
}
3.2 Invariants

line_start <= line_end

scene_id matches your scene ID format (01-02-01, etc.)

Prefer at least one quote-backed span for canon assertions.

type=inferred permitted only when allowed by the consuming schema or registry flag.

3.3 Where It Lives

Always allowed on timeline events.

Allowed in .meta.json entries per-ID.

Not inline in canon payloads, except where explicitly designed (e.g., timeline).

4) Tags — Structure & Registry
4.1 Tag Block (shared schema)
{
  "type": "object",
  "patternProperties": {
    "^[a-z_]+$": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9_]+$" },
      "uniqueItems": true
    }
  },
  "additionalProperties": false
}

Use via $ref in any schema field named tags.

4.2 Tag Registry (authoritative list)

Each tag class (bucket) maps to an array of tag definitions.

{
  "skills": [
    { "tag": "teleportation", "status": "approved", "allow_inferred": false, "aliases": ["blink"], "notes": "Strict; avoid metaphorical use." }
  ],
  "affinity": [
    { "tag": "void", "status": "approved", "allow_inferred": true }
  ]
}

Rules

Tags used in canon must exist in the registry, or be explicitly approved during promotion.

allow_inferred=false → don’t use tag without a quote-backed source_ref.

Registry is where synonyms/aliases and guidance live.

5) Links — Graph Relations

Use links[] to connect IDs.

{
  "links": [
    { "type": "upgrades_to", "target": "sn.meditation.rank2", "reason": "Observed advancement" },
    { "type": "related_to", "target": "sf.inner_peace" },
    { "type": "granted_by", "target": "eq.cloak_of_phasing" }
  ]
}

Note: links live in .meta.json so the canon stays lean.

6) Validation Rules (summary)

IDs are required on all referencables; must be unique; lower_snake segments with type prefix.

Cross-file references must use IDs (not labels).

Tags must validate against the shared tag schema; values must exist in registry unless promoted.

Provenance on events must include at least one source_ref (quote-backed preferred).

allow_inferred=false prevents tag use without quotes.

Sidecars must validate against their schemas (index_meta, review, provenance).

7) Workflows (recipes)
7.1 Add a new skill (minimal)

Create sf.* if family doesn’t exist.

Add sn.* node to records/ with minimal fields + optional tags.

Add .meta.json entry with index_meta and (ideally) a source_ref.

If discovered in a scene, add timeline event referencing node_id with source_ref.

7.2 Enrich an existing skill after new chapter

Append a new timeline event with observed params + source_ref.

If facts become stable, update the node’s canon fields.

Log change in record_log.

7.3 Create an upgrade path

Add new sn.* ID (e.g., sn.spectral_displacement.rank2).

In old node’s .meta.json, add links[{type:"upgrades_to", target:"sn...rank2"}].

Optionally add links[{type:"upgrades_from", target:"sn...rank1"}] in the new node.

7.4 Promote a tag candidate

Run tools/promote_tags.py → pick tag + class; set status.

Decide allow_inferred.

Write registry entry with index_meta in its .meta.json.

(Optional) enforce that scenes using a not-yet-approved tag fail validation.

8) Edge Cases & Policies

Renames: never change IDs; change display names only. Add aliases where needed.

Retcons: add new events with later source_ref; annotate conflicts in .review.json.

Conflicting sources: keep both source_refs; reviewer picks the active interpretation.

Splits/merges: create new IDs; link old → new via links and keep history in record_log.

9) Open Questions (trackers)

Do we want .provenance.json everywhere or only for dense sources?

Do we standardize event_id format repo‑wide?

Where to store long quotes (per‑event only, or also in sidecars)?

10) Glossary

Canon payload: the lean JSON inside records/ that RAG consumes.

Sidecar: a sibling JSON file (e.g., .meta.json) with audit/provenance/review.

Registry: authoritative list of allowed values (e.g., tags).

source_ref: reference to where a fact was observed (scene + line span, etc.).

ID: the stable string that everything else points at.

11) Appendix — Mini Schemas
11.1 source_ref (fragment)
{
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": { "enum": ["scene", "wiki", "user", "inferred", "external"] },
    "scene_id": { "type": "string", "pattern": "^\\d{2}-\\d{2}-\\d{2}$" },
    "line_start": { "type": "integer", "minimum": 1 },
    "line_end": { "type": "integer", "minimum": 1 },
    "quote": { "type": "string", "maxLength": 400 }
  },
  "allOf": [
    { "if": { "properties": { "type": { "const": "scene" } } },
      "then": { "required": ["scene_id", "line_start", "line_end"] } }
  ]
}
11.2 tags (shared)
{
  "type": "object",
  "patternProperties": {
    "^[a-z_]+$": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9_]+$" },
      "uniqueItems": true
    }
  },
  "additionalProperties": false
}
12) Is this approach rare?

In big, mature data/ML systems: this is the norm (IDs + sidecars + registries).
In hobby or early projects: most folks skip IDs, jam everything inline, and regret it later.
You’re just doing the grown‑up version early, which saves you months of churn. Not flashy — but very senior.

13) Quick Checklist (pin this)




Dropped a full, plain‑English spec into a doc you can keep tweaking: “Provenance System Contract (v1)”. It spells out IDs, sidecars, source_ref rules, tags, validations, workflows, and tons of examples so Future‑You won’t want to strangle Past‑You.

Want any bits expanded—like a naming table for every ID type, or a stricter source_ref schema with if/then rules?

You said:
codex:



This convo is on the right track—the four-layer metadata model plus stable IDs gives you everything you need for provenance, incremental enrichment, and future RAG/LLM tooling. A few things I’d reinforce or suggest:

Lock in a shared ID contract now (naming, where required, allowed chars). Even if you stick with human-readable IDs, having it documented in docs/provenance_contract.md or similar keeps future entries consistent and lets validators enforce it.
Consider adding the change-history log (record_log[]) to your sidecars sooner rather than later. You don’t have to model every old value, but capturing who/when/why something changed makes the graph replayable and prevents silent edits.
Source refs might benefit from a source_type field now, even if everything is scene today. Future you won’t have to retrofit when wiki or user-generated sources creep in.
For tag usage, think about optional per-tag justification (even a single string) inside the scene/timeline payloads; reviewers and future LLM audits will thank you.
When you document the system, call out where RAG relevance lives vs. training relevance. Even if it’s one JSON doc today, naming the intent will keep it from becoming a grab bag.
You’ve basically got a knowledge graph hiding inside JSON files—stable IDs plus sidecars is the right way to get the relational structure without losing your lightweight payloads. Document the conventions, start wiring validators to enforce them, and you’ll be set.

do you have ideas on how else to handle it? better ways to do this?


A few alternative patterns you might kick around while everything’s still fluid:

Primary record + entry bundle. Instead of scattering sidecars, treat each canonical ID as a “bundle” directory: /records/skills/sn.spectral_displacement.v1/record.json, /meta.json, /review.json, /links.json. It keeps payload vs. meta separation, but co-locates everything for that node and makes tooling discovery trivial.

Event log as ground truth. Make timeline-like “event streams” the authoritative source; derive the current record snapshot via reducers. That’s heavier up front, but it gives you version history, diffing, and provenance for free. Canon JSON becomes a cached view.

Normalized graph store. Push IDs + relationships into a thin JSON graph (nodes array + edges array). Wrapper CLIs spit out records/*.json for human-friendly editing, but validators and RAG work off the normalized graph. Lets you add new relationships without touching the canonical files.

Metadata registry. Maintain one meta/index.json keyed by ID that aggregates review state, RAG weights, provenance references, etc. Everything meta lives there; individual records stay pristine. Makes it easy to stream meta into tooling without opening lots of sidecars.

JSON-LD / linked-data flavor. If you already think in nodes and edges, you could lean into a simple JSON-LD schema for canonical entries. That preserves human readability but lets you bring off-the-shelf graph tooling later.

State “snapshots” per timeline. Instead of storing all historical facts in the record, maintain timeline snapshots keyed by scene/event (snapshot_id → current skill states). Records just describe the static entity; timeline snapshots tell you “what was true when,” and RAG planners can pick whichever view they need.

None of these invalidate your current plan; they’re just different knobs on how much you normalize, how you organize meta, and where you want the source of truth to live. You can even mix: start with your sidecars + IDs, and if maintaining them gets messy, promote that data into a bundle layout or registry.
ChatGPT said:

ohh Codex is cooking with gas here. Those alt patterns are all legit—just different knobs on “how normalized vs how human‑friendly” you want the repo to be. Here’s the quick, no‑BS tour, then I’ll tell you what I’d adopt now vs. park for later.

Which pattern does what (fast take)

1) Bundle directories (one folder per ID)

Shape: records/skills/sn.spectral_displacement.v1/{record.json, meta.json, review.json, links.json}

Wins: zero hunting; tooling is trivial (“open folder, you have everything”). Great once a node accrues lots of meta.

Cost: directory explosion; harder bulk edits; more Git noise.

Verdict: 👍 Future‑me loves it; present‑me can wait. Migrate when a few nodes get “thicc”.

2) Event log as ground truth (event‑sourced)

Shape: append‑only events; “records” are just materialized snapshots from reducers.

Wins: perfect history, diffs, provenance—free. Time‑travel is native.

Cost: complexity; you need reducers, snapshotting, and tooling from day one.

Verdict: 🔥 Architect‑sexy, but heavy right now. Do a mini version: keep your timelines authoritative for changes, and write a tiny “projector” CLI later to build state.

3) Normalized graph store (nodes/edges JSON)

Shape: graph/nodes.json, graph/edges.json; records become views.

Wins: adding new relationships is painless; graph queries are easy; RAG precompute is nice.

Cost: dual truth surfaces; humans don’t like editing nodes/edges by hand.

Verdict: 🧠 Great for analytics and RAG later. For now, your links[] + IDs already give you 80% of the graph—export a normalized view when you need it.

4) Metadata registry (one big meta index)

Shape: meta/index.json keyed by ID with review state, weights, provenance pointers.

Wins: blazing‑fast lookups; one file to stream into tools; no sidecar chasing.

Cost: one giant lock file; merge conflicts; single hot spot.

Verdict: 🤏 Consider a lightweight meta/index.json cache that’s generated (not source‑of‑truth). Keep sidecars canonical.

5) JSON‑LD / linked data

Wins: off‑the‑shelf graph tooling; semantics carry further.

Cost: cognitive overhead; more verbose; you’ll be fighting the format while still designing content.

Verdict: ❄️ Cool later, not now. Your current JSON + IDs is already “LD‑ish.”

6) Timeline snapshots per scene

Shape: snapshot of “current world state @ scene X”.

Wins: RAG gold; projections get trivial.

Cost: storage and generation; you need a projector.

Verdict: ✅ Yes—but derive them with a projector tool; don’t hand‑author.

My recommendation (pragmatic, today)

Stick with your current plan and bolt on a few targeted upgrades:

Lock the ID contract (now)

prefix.segment.segment (snake_case), immutable, required anywhere referencable.

Add a tiny validator that screams if any cross‑ref uses a label instead of an ID.

Keep sidecars, add structure

Make record_log[] mandatory in .meta.json.

Add source_ref.type (scene|wiki|user|inferred|external) now so we don’t retrofit later.

Allow links[] in .meta.json only (canon stays lean).

Add a tiny meta index (generated)

tools/build_meta_index.py → emits z_artifacts/meta_index.json with { id: { path, review_status, confidence } }.

Use it for CLIs/UI speed; never hand‑edit it.

Do the projector, not full event‑sourcing

tools/projector.py --character pc.jake --through 03-14-01 → computes state from timeline events.

Later, if this becomes your favorite thing, you can promote events to be the ground truth.

Plan the bundle layout as an opt‑in migration

When a node’s sidecar gets heavy, run tools/migrate_to_bundle.py sn.meditation.rank1 to move that one node into a folder. Mixed modes are fine.

Optional nicety: per‑tag justification on scenes/timeline

tags_justification: { "stealth_attack": "ambushed from shadows" } helps reviews and LLM audits.

Why this mix?

You get the developer ergonomics you want now (simple files, sidecars, IDs) and a clear upgrade path if/when scale hits:

projector gives you snapshots (RAG‑friendly) without forcing event‑sourcing everywhere

generated meta index gives you tool speed without creating a new “truth”

bundle layout is a safety valve for “hot” nodes, not a repo‑wide migration

Tiny checklist to pin it down

 Add an ID Contract section to the provenance doc (prefixes, regex, required places).

 Update provenance.schema.json to include source_ref.type.

 Make record_log[] required in .meta.json schema.

 Add shared/tags.schema.json $ref to any schema that carries tags.

 Write tools/build_meta_index.py (generated cache).

 Spec tools/projector.py (minimal first: skills + params).

 Add a rule in validators: cross‑file references must be by id (not label).

If you want, I’ll draft the ID Contract block and the micro‑schemas (updated source_ref + .meta.json) next, then we wire the validators.
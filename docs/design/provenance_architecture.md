# 🧱 PHI Provenance Architecture: Future Patterns & Migration Strategy

**Status:** Informational (v1.0)
**Updated:** 2025-10-07
**Maintainer:** PHI Design Lead
<!-- ─────────────────────────────────────────────────────────────────────────────── 📘 DESIGN DECISION RECORD
(DDR) ─────────────────────────────────────────────────────────────────────────────── This document captures
architectural reasoning, trade-offs, and forward-looking migration paths for the PHI Provenance System. It is
NOT schema-binding or enforced by validators. Use it as design guidance and historical record only.
───────────────────────────────────────────────────────────────────────────────
-->
---

## 🎯 Purpose

This document captures the *architectural reasoning* behind the current PHI provenance system and records
**future evolution paths**. It is **not a contract** — no validator depends on it — but it explains *why* the
system is structured this way and *how* it can scale without breaking canon.

---

## 🧩 Current Baseline Model

| Layer | Function | File shape |
| --- | --- | --- |
| **Canon payload** | Minimal, quote-free facts | `records/**/*.json` |
| **Sidecars** | Provenance metadata, `record_log[]`, reviews | `.meta.json`, `.review.json` |
| **Timeline** | Append-only event history per character/entity | `records/characters/*/timeline.json` |
| **Registry** | Central vocabularies and tag metadata | `tag_registry.json`, `tag_registry.meta.json` |

### Principles

- Immutable, human-readable stable IDs (`prefix.segment.segment`)
- Append-only record logs for all canonical nodes
- Provenance captured by `source_ref[]`
- Optional links graph (`links[]`) for relationships
- Small, fast, JSON-only footprint for LLM friendliness

---

## 🚀 Alternative Patterns (Evaluated)

| Pattern | Core idea | Pros | Cons | Decision |
| --- | --- | --- | --- | --- |
| **Bundle directories** | One folder per entity (`sn.skill.rank1/{record,meta,review}`) | Everything colocated, trivial discovery | Directory sprawl, Git churn | Adopt later for “thicc” nodes only |
| **Event-sourced ground truth** | Timelines act as source of truth; records are projections | Perfect provenance, native diffing | Requires reducers + snapshotting infrastructure | Postpone; simulate with `projector.py` |
| **Normalized graph store** | Central `nodes.json` + `edges.json` encode relationships | Easy analytics and graph queries | Not human-friendly; dual source of truth | Export-only for analytics |
| **Metadata registry (`index.json`)** | Master index for review/provenance state | Blazing-fast lookups, tooling-friendly | Merge conflicts; single hot spot | Generate read-only cache only |
| **JSON-LD / linked data** | Semantic node/edge definitions | Interoperable with graph tooling | Verbose, overkill | Defer indefinitely |
| **Timeline snapshots** | Derived “world state” per scene | Ideal for RAG and diffing | Requires projector tool | ✅ Implement via `projector.py` |

---

## ✅ Adopted Now

1. **Lock the Stable ID Contract**

   - Format: `^(sn|sf|eq|cl|rc|pc|loc|tag|ev)\.[a-z0-9_]+(\.[a-z0-9_]+)*$`
   - Required on all referencables
   - Validators reject label-based cross-refs

1. **Make `record_log[]` Required**

   - Mandatory in all `.meta.json` sidecars
   - Enables diffing, change history, and replay audits

1. **Add `source_ref.type`**

   - Enum: `scene | wiki | user | inferred | external`
   - Future-proofs provenance without migration later

1. **Allow `links[]` Only in `.meta.json`**

   - Keeps canon clean; graph relationships live in metadata

1. **Add a Generated Meta Index**

   - `tools/build_meta_index.py` → emits `z_artifacts/meta_index.json`

```json
{
  "sn.meditation.rank1": {
    "path": "records/skills/sn.meditation.rank1/record.json",
    "review_status": "approved"
  }
}
```

   - Never hand-edited; cache only

1. **Implement `projector.py`**

   - Command:

```bash
tools/projector.py --character pc.jake --through 03.14.01
```

   - Replays timeline → builds current world state snapshot
   - Powers RAG queries without rewriting canon

1. **Optional Tag Justifications**

   - Non-canon reviewer notes:

```json
"tags_justification": {
  "spectral": "teleport effect described as phasing out",
  "ambush": "attacked from behind"
}
```

   - Store in `timeline.json` or `.review.json`; later schema-ize under `review.schema.json`

---

## 🪄 Migration Paths (Future Options)

| Feature | When to enable |
| --- | --- |
| **Bundle layout** | When a node’s meta/review exceeds ~5 KB or gains multiple revisions |
| **Event-sourced ground truth** | When timelines exceed ~10k events per entity |
| **Normalized graph export** | When external analytics or RAG pre-compute is needed |
| **Metadata registry** | When CLIs slow down parsing thousands of sidecars |
| **Snapshot cache** | When projector becomes standard for RAG workflows |

---

## 🧠 Why This Mix Works

| Goal | Mechanism |
| --- | --- |
| Human-friendly editing | Flat JSON files, minimal boilerplate |
| Machine-queryable | Stable IDs, `links[]`, and generated indexes |
| Versioned & auditable | Mandatory `record_log[]` entries |
| RAG-ready | Projector snapshots derived from timelines |
| Scalable & upgradable | Optional bundle layout plus export-oriented graph artifacts |

---

## 🔧 Next Implementation Steps

1. **Schema Updates**

   - `meta.schema.json`: `record_log[]` required
   - `source_ref.schema.json`: include `"type"` field
   - Add shared `tags.schema.json` `$ref` in all tag-carrying schemas

1. **Validators**

   - `validate_all_metadata.py`: enforce ID usage
   - `validate_provenance.py`: enforce `source_ref[]` rules
   - `validate_record_log.py`: enforce append-only `record_log[]`

1. **Tools**

   - `build_meta_index.py`: generate cache
   - `projector.py`: reconstruct state from timeline events
   - `migrate_to_bundle.py`: move “thicc” nodes into folder layout

---

## 📚 Related Docs

- [`contracts/id_contract.md`](../contracts/id_contract.md)
- [`contracts/record_log_contract.md`](../contracts/record_log_contract.md)
- [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)
- [`design/storage_layout.md`](storage_layout.md)
- [`design/graph_links.md`](graph_links.md)
- [`design/pipeline_flow.md`](pipeline_flow.md)

---

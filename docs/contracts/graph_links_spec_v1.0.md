# Graph Links Spec (PHI) — v1.0

**Status:** Final  
**Updated:** 2025-10-10

## Purpose

Define a **sidecar-only** `links[]` structure for lightweight, typed edges between PHI IDs.  
Links provide local graph context without bloating canonical payloads or timelines.

- Canon stays semantic; contextual glue lives in sidecars. :contentReference[oaicite:4]{index=4}  
- IDs everywhere; never use names. :contentReference[oaicite:5]{index=5}  
- This spec complements (and does not replace) the Ontology’s relationship records. :contentReference[oaicite:6]{index=6}

## Placement

- **Allowed:** `.meta.json` sidecars only  
- **Forbidden:** `record.json`, `timeline.json`, `.review.json`, `.provenance.json`

`.meta.json` is the authoritative sidecar for canon context (record log, provenance, lightweight edges).  
`.review.json` and `.provenance.json` retain their respective QA / reverse-index roles and do not host links. :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}

## Allowed `type` values (closed set)

- `upgrades_to` — source node progresses to a successor node  
- `granted_by` — source was granted by a granter or event  
- `related_to` — symmetric, non-hierarchical association  
- `derived_from` — source is derived from / synthesised from the target

Editorial history edges (`replaces`, `split_from`, `merged_into`, …) remain governed by the ID & Record Log contracts. :contentReference[oaicite:9]{index=9} :contentReference[oaicite:10]{index=10}

## Object model

```json
"links": [
  {
    "type": "upgrades_to",
    "target": "sn.meditation.rank2",
    "reason": "System rank-up acknowledged in 01.05.01"
  }
]
```

- `type` — required; one of the allowed values above.  
- `target` — required; **stable ID** validated by the shared ID schema. :contentReference[oaicite:11]{index=11}  
- `reason` — optional; short human-readable note (no quotes/coords; provenance remains at sidecar level).

### Direction semantics

- `upgrades_to`: source → successor (rank/tier progression)  
- `granted_by`: source → granter (typically `ev.*`, may be `cl.*`, `pc.*`, `eq.*`, `sys.*`)  
- `related_to`: symmetric; tools should treat `(A,B)` equivalent to `(B,A)`  
- `derived_from`: source → antecedent

## Deduplication & normalisation

- `links[]` behaves as a **set**. A sidecar MUST NOT contain duplicate `{type, target}` pairs.  
- Validators MUST reject duplicates.  
- Tooling SHOULD sort links by `type`, then `target`, for stable diffs.

## Provenance

Links do **not** carry per-link `source_ref`.  
If justification is required, cite it using the existing sidecar-level `source_ref[]`.

## Relationship to other contracts

- **Ontology:** Use `links[]` for pragmatic, per-record edges; rely on ontology relationship records for global graphs.  
- **Skills:** Node lineage and rank upgrades are canon. Use `links[]` to annotate conveniences such as `upgrades_to` or `related_to`.  
- **Provenance:** Sidecars carry `record_log[]`, `source_ref[]`, and now `links[]`; canon payloads remain provenance-free. :contentReference[oaicite:4]{index=4}

## Validation rules

Validators MUST ensure:

1. `links[]` only appears in `.meta.json`. Presence in `record.json`, `timeline.json`, `.review.json`, or `.provenance.json` is an error.  
2. Each entry has `type ∈ {upgrades_to, granted_by, related_to, derived_from}`.  
3. `target` conforms to the shared ID schema.  
4. `reason` (if provided) is a string (≤ 200 chars recommended).  
5. Duplicate `{type, target}` pairs are rejected.

## Examples

### Skill node sidecar (`records/skills/sn.meditation.rank1/meta.json`)

```json
{
  "id": "sn.meditation.rank1",
  "record_log": [
    { "action": "added", "by": "assistant", "date": "2025-10-08" }
  ],
  "source_ref": [
    { "type": "scene", "scene_id": "01.02.01", "line_start": 120, "line_end": 130 }
  ],
  "links": [
    { "type": "upgrades_to", "target": "sn.meditation.rank2" },
    { "type": "granted_by", "target": "ev.jake.01.02.01.skill_acquired_meditation", "reason": "Tutorial award" },
    { "type": "related_to", "target": "sf.focus" },
    { "type": "derived_from", "target": "sf.meditation" }
  ]
}
```

---

# 🆔 PHI Stable ID Contract

Updated: 2025-10-05

## Purpose
This contract defines how stable IDs work in the Primal Hunter Index (PHI) project. It enables traceable cross-references, canonical immutability, and timeline-based replay across JSON records, sidecars, timelines, and tools.

## ID Format

- **Regex:** `^(sn|sf|eq|cl|rc|pc|loc|tag|ev)\.[a-z0-9_]+(\.[a-z0-9_]+)*$`
- **Structure:** `prefix.segment[.subsegment...]`
- **Separator:** Dot (`.`)
- **Style:** All lowercase, `snake_case` segments

## Allowed Prefixes

| Prefix | Meaning                    | Example                          |
|--------|-----------------------------|----------------------------------|
| `sn.`  | Skill node                 | `sn.meditation.rank1`            |
| `sf.`  | Skill family               | `sf.meditation`                  |
| `eq.`  | Equipment                  | `eq.cloak_of_phasing`            |
| `cl.`  | Class                      | `cl.void_warden`                 |
| `rc.`  | Race                       | `rc.dryad`                       |
| `pc.`  | Character (person)         | `pc.jake`                        |
| `loc.` | Location                   | `loc.haven_city`                 |
| `tag.` | Internal tag key reference | `tag.skills.teleportation`       |
| `ev.`  | Timeline event             | `ev.jake.01_02_01.a`             |

## Rules

- All referencable entries must have an `id`
- All cross-file references (timeline, links, tags) **must** use `id`, not name/label
- IDs are **immutable**: renames create a new ID and are linked with `links[]`

## Validator Support

- `tools/validate_ids.py` will ensure:
  - IDs are present
  - IDs match the contract regex
  - No label-based references in timeline/meta/scene files

## Justification

This ID scheme is foundational to enabling:
- Provenance tracking via `source_ref[]`
- Safe sidecar layering (`meta`, `review`, `provenance`)
- Canon diffing
- LLM training and tagging pipelines
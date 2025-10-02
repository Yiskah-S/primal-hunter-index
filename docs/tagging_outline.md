# Tagging Guide (Draft Outline)

This outline captures the agreed-upon parts of the tagging workflow. Promote sections to a full guide once the review flow is finalized.

## Purpose & Principles

- Tags normalize synonyms and support faceted filtering (`affinity + stealth + lore`).
- Tags feed few-shot prompts and annotate implicit meaning not captured by names.
- Tags are lowercase snake_case; registry enforces casing and uniqueness.

## Tag Registry Structure

- `records/tag_registry.json` defines tag metadata.
- `schemas/tag_registry.schema.json` enforces classes, descriptions, allowed flags.
- Tag classes (`topic`, `entity_type`, `function`, `narrative`, `system`) categorize usage.

## Tag Usage Rules

- Only tags defined in the registry may be used; validator rejects unknown tags.
- Scene tags live in `records/scene_index/...`; skills use `tags[]` for semantic grouping.
- Keep tags declarative (what happens, not how we infer) — derived relationships stay out of canon files.

## Examples (Stealth Pilot)

| Use Case                                 | Tags                                                                                  |
|------------------------------------------|---------------------------------------------------------------------------------------|
| Character uses Stealth skill             | `stealth`, `skill_usage`, `stealth_skill`, `dark_affinity` (if revealed)              |
| Lore explanation about Stealth mechanics | `stealth`, `skill_lore`, `mechanic`, `rules`                                          |
| Affinity linkage revealed                | `dark_affinity`, `affinity_reveal`, `stealth`, `skill_lore`                           |
| Combat emphasizing stealthy behavior     | `stealth`, `scene`, `combat`, `skill_usage`                                          |

## Validator Hooks (Planned)

- Ensure every tag reference matches the registry.
- Warn on ambiguous or duplicate tags (e.g., `dark` vs `dark_affinity`).
- Optional: allow per-tag metadata (`{"tag": "foo", "inferred": true}`) if needed.

## Open Questions (track in z_notes/tagging.md)

- Should scene tags capture inferred traits from context?
- Is tag namespacing required to avoid drift?
- Do we need per-tag provenance or reviewer metadata?

Promote this outline into full documentation once the tagging review loop (propose → review → commit) is live.

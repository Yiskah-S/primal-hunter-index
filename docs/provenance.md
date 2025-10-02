# Provenance Guide

Every canonical dataset in this repository adheres to a simple rule:

> **If it asserts a canon fact, it must include a `source_ref` block.**

That block records the scene and line span in the source text so every fact can be quote-backed.

## Where Provenance Is Required

| Dataset                                 | Rationale                                     |
|-----------------------------------------|-----------------------------------------------|
| `records/skills.json`                   | Mechanics, upgrades, lore                     |
| `records/equipment.json`                | Item descriptions, origins                    |
| `records/titles.json`                   | Acquisition method, effects                   |
| `records/classes.json`                  | Class reveals, bonuses                        |
| `records/affinities.json`               | Affinity usage, lore                          |
| `records/races.json`                    | Species traits, tiers                         |
| `records/locations.json`                | Descriptions, first appearances               |
| `records/zone_lore.json`                | Regional revelations                          |
| `records/system_glossary.json`          | Term introductions                            |
| `records/global_event_timeline.json`    | Major events and outcomes                     |
| `records/global_announcement_log.json`  | System messages and context                   |
| `records/tiers.json`                    | Tier system explanations                      |
| `records/stat_scaling.json`             | Stat interactions or tests                    |
| `records/affiliations.json`             | Faction introductions, philosophies           |
| `records/creatures.json`                | Creature sightings, behavior                  |

Any new canon dataset should follow the same pattern.

## Schema Expectations

- Canon entries include a boolean `canon` flag.
- Every canon entry provides `source_ref`, either a single object or an array of `source_range` objects:

```json
{
  "canon": true,
  "source_ref": {
    "scene_id": "01-02-01",
    "line_start": 111,
    "line_end": 120
  }
}
```

All schemas now import `schemas/shared/provenance.schema.json`:

- `$defs.source_range` (scene id + line bounds)
- `$defs.source_ref` (single or array of ranges)

## Validator Enforcement

`tools/validate_all_metadata.py` checks:

1. Schema compliance (`canon` + `source_ref`).
2. Scene existence (`scene_id` present in `records/scene_index`).
3. Line spans within the scene’s `start_line`/`end_line`.

Failing entries produce actionable error messages (file, entry pointer, violation).

## UI Support

`tools/json_editor/app.js` ensures:

- `source_ref` fields are visible and editable for every dataset.
- Scene previews appear (title, summary, line range) to help pick the correct span.
- All canon datasets load under the editor for consistent workflows.

## Workflow Tips

- Use `tools/search_skill_mentions.py` to gather all chapter snippets that mention an entity. The generated `manifest.json` lists line numbers so you can fill out `source_ref` accurately.
- Treat the Golden Skill Spotlight as a canary: fully populate one skill entry and verify you can source every field. Adjust the schema if a canonical fact can’t be quoted.
- Record provenance decisions or edge cases in `z_notes/prov.md` before promoting them to this guide.

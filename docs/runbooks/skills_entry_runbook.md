Title: Skill Entry Runbook (PHI)  
Status: Living  
Linked Schema: schemas/skills.schema.json  
Updated: 2025-10-08  

This guide distils the working notes for capturing canon skill data into repeatable steps you can follow while reading chapters.

## Granted By

- Record every origin event that awards, upgrades, or replaces the skill.
- Choose one of the controlled types from `schemas/shared/granted_by.schema.json`:
  - `system` — automatic awards during tutorials, system messages, global announcements.
  - `class_upgrade` — class evolution, promotion, or specialization milestones.
  - `title` — titles that grant the skill (note the title name in `name`).
  - `item` — items or equipment that bestow the skill.
  - `blessing` — divine, patron, or faction blessings.
  - `quest` — explicit quest rewards.
  - `loot`, `crafting`, `vendor` — tangible sources that hand over the skill.
  - `other` — edge cases; always fill `notes` to explain.
- `name` should be the in-world label (`Introduction Entity`, quest name, etc.). Use `notes` to describe nuances such as “granted to all tutorial archers simultaneously.”
- Prefer one grant object per distinct narrative event even if the same source applies to multiple skills.

## Provenance & Scene IDs

- `source_ref.scene_id` is the canonical scene identifier; keep it in `BB-CC-SS` format.
- Capture the precise quote span with `line_start` and `line_end`. If the mention is a single line, set both to the same value.
- When provenance comes from dialogue describing a previous event, cite the dialogue scene, not the flashback location, and clarify the context in `notes`.

## Effects Block

- `effects.proficiency_with` is a controlled list of lowercase plurals (`bows`, `crossbows`). Add new values sparingly and document them in the tag registry if they become common.
- `effects.stat_synergy` only lists stats explicitly mentioned in canon. Leave absent stats out rather than zeroing them.
- Use `passive_benefit` for short prose summaries that link the mechanic to a stat (“Minor boost to ranged attacks derived from Agility and Strength”).

## Behavior Block

- `activation_method` mirrors the phrasing the System uses (“Focus on a target”, “Passive”).
- `instinctive_knowledge` is `true` when canon confirms the user “just knows” how to use the skill.
- `user feedback` captures any experiential description (“Vision sharpens from normal to high clarity”).

## Tags

- Stick to lowercase snake_case tags registered in `records/tag_registry.json`.
- If you invent a new tag, add it to the registry before committing the skill entry.
- Use inferred tags sparingly; prefer explicit canonical justification.

## Validation Checklist

1. Run `make validate` after editing skills to confirm schema + provenance.
2. Execute `pytest tests/schema/test_roundtrip_golden.py` to keep the Basic Archery golden record passing.
3. If schema changes were required, capture them with `python3 tools/diff_schemas.py schemas skills.schema.json` before committing.

Cross-file alignment keeps the skill catalog trustworthy; update this document whenever the schema or workflow evolves.

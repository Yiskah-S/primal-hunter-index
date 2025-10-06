# 📜 PHI Record Log (`record_log[]`) Contract

Updated: 2025-10-05

## Purpose

The `record_log[]` field tracks the change history of each canon entry.

It lives in `.meta.json` and is required for all entries with a stable ID.

## Format

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-06" },
  { "action": "approved", "by": "user", "date": "2025-10-07" },
  { "action": "edited", "by": "user", "field": "description", "from": "Old", "to": "New", "date": "2025-10-09" }
]
```

## Required Fields

- `action`: `"added"`, `"edited"`, `"approved"`, `"rejected"`, `"deleted"` (enum)
- `by`: `"user"` or `"assistant"`
- `date`: `"YYYY-MM-DD"` (ISO)
- Optional: `field`, `from`, `to`, `notes`

## Why It Matters

- Enables safe updates over time
- Prevents silent overwrites
- Lets you replay a node's history
- Enables Codex to provide rationale or flag risky diffs

## Storage

Stored in the `.meta.json` file for the ID.

## Enforcement

- Will be required by `meta.schema.json`
- All entries in `records/` must have one
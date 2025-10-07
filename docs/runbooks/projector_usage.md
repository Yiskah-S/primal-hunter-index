# DRAFT ACTIVE DISCUSSION IN PROGRESS
## IDEAS:

### 2.3 Timelines (records/characters/*/timeline.json)

✅ Status: Already fully integrated
🧩 Where: provenance_contract_v2.0.md (sections 2 + 6) and indirectly in record_log_contract_v1.1.md

Nothing missing.
We already require source_ref[] and tags[] on every event and reference IDs (skill_id, eq_id, etc.) instead of labels.

Minor improvement idea (optional):
We could explicitly restate this example in docs/runbooks/projector_usage.md once that’s created — “How to add new timeline events properly.”
📍Add to TODO list for runbook scaffolding.

### 2.3 Timelines (`records/characters/*/timeline.json`)

* Events always reference `id`s (e.g. `node_id`, `eq_id`)
* Each event can carry its own `tags`, `source_ref`, and metadata

---

🧩 2.3 Timelines (events)

✅ Already implemented, both in:

provenance_contract_v2.0.md (enforcement rules)

projector_usage.md (event examples and commentary)

New here: explicit "observed_params" object — worth highlighting.

📍Action:
Add to projector_usage.md →

“Optional observed_params block can record dynamic numerical data (e.g. duration, cooldown) extracted from narrative events.”

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
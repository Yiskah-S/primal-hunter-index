# Draft: Active Discussion in Progress

## Ideas Backlog

## Links (Graph-Style Relations)

💡 This is the interesting survivor.

"links": [
  { "type": "upgrades_to", "target": "sn.meditation.rank2" },
  { "type": "granted_by", "target": "eq.cloak_of_phasing" }
]

This feature was discussed but not explicitly retained in our current finalized contracts.
We have implicit linking via family_id and timeline events, but no formal contract defining relational links[].

🧠 Why keep it?

Enables graph queries (skill trees, dependencies, “who granted what”)

Keeps IDs stable but relationships evolving

Becomes key later for the SQL layer or bundle inspector (bundle_viewer.py)

🟡 Recommendation:
We should define this in the future docs/design/graph_links.md or fold it into storage_layout.md under “Optional Bundle Extensions.”
For now, note it as “reserved for future schema expansion.”

📍TODO:
→ Add to storage_layout.md as an optional links.json or field inside .meta.json  
→ Cross-link from id_contract.md (since it defines inter-ID references)

Lives in `.meta.json`:

```json
"links": [
  { "type": "upgrades_to", "target": "sn.meditation.rank2" },
  { "type": "granted_by", "target": "eq.cloak_of_phasing" }
]
```

---

🧠 The links[] array

Already flagged earlier for inclusion in graph_links.md.
The "reason" field here ("Observed rank-up in arc 4") is an excellent addition — keep it as optional commentary when we formalize that schema.

📍Action:

Add "reason" (string, optional) to your draft schema in graph_links.md.

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
        "scene_id": "03.14.01",
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

🔗 5) Links — Graph Relations

Reinforces and expands what we already migrated to graph_links.md.

But this old snippet adds a new relationship type we hadn’t captured before:

Use links[] to connect IDs.

{
  "links": [
    { "type": "upgrades_to", "target": "sn.meditation.rank2", "reason": "Observed advancement" },
    { "type": "related_to", "target": "sf.inner_peace" },
    { "type": "granted_by", "target": "eq.cloak_of_phasing" }
  ]
}

Note: links live in .meta.json so the canon stays lean.

🟡 Action:
Add "related_to" to the list of allowed link types in your graph_links.md draft table.

That gives us the set: `upgrades_to`, `granted_by`, `related_to`, and potentially `derived_from`.

Also, it reiterates:

“links live in .meta.json so the canon stays lean.”
✅ That exact phrasing should go in your storage_layout.md under “Bundle Layout → Optional Files.”

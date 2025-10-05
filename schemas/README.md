# 📐 `schemas/` Directory – Primal Hunter Index

This folder defines the shape of all canonical data used in the Primal Hunter Index project.  
Everything in `canon/`, `records/`, and `fixtures/` must validate against these schemas before being committed.

---

## 🧱 Core Concepts

### ✅ `skill_family.schema.json`
Represents the *idea* of a skill. Global, not character-specific.  
Think: "Meditation exists and is considered a Utility skill."

- `id`: `"skill:meditation"`
- `tags`: Useful for grouping (e.g. `["focus", "mind"]`)
- `source_ref[]`: Required. Must cite a scene where the skill was mentioned.

---

### 🌱 `skill_node.schema.json`
Represents a specific *variant or evolution* of a skill.  
Example: `"Meditation [Common]"`, `"Meditation [Apex]"`

- `param_rules[]`: Describes how cost or effects scale (via formula or heuristic)
- `upgrades_to[]`: Lists valid evolution paths and their conditions
- `source_ref[]`: Required. Canon only if quote-backed.

---

### 📘 `timeline_event.schema.json`
Character-specific log of state changes over time.  
Tracks things like:

- Skill acquisitions
- Observed param values
- Class or tier changes
- Equipment gained or used

Used in per-character files like:

```
records/characters/Jake/timeline.json
fixtures/arnold/story_timeline.json
```

Also supports:

- `context`: State at the time (e.g. level, gear, class)
- `inference`: Optional justification for inferred (non-quote-backed) observations

---

### 🔍 `shared/source_ref.schema.json`
Shared object for all quote-backed facts.

- `scene_id`: `"BB-CC-SS"` format (e.g. `"01-02-03"`)
- `line_start` / `line_end`: Line numbers in the scene file
- `quote` (optional): Direct quote for human use or GPT scaffolding

Used in:
- `skill_family`
- `skill_node`
- `timeline_event`

---

## 🧪 How to Validate

Use `validate_instance()` or `tools/validate_all_metadata.py`  
All commits must pass schema validation via pre-commit hook before merging.

---

## 🚧 Future Plans

- Add `shared/condition.schema.json` to validate `when` rules
- Refactor `param_rules` to support logical AND/OR combinations
- Enforce allowed keys in `context`

---

## 🧠 Why This Exists

Because 3 months from now you won't remember what `param_rules[].when` was supposed to do.

This README is your brain's external backup for schema intent, boundaries, and design assumptions.  
Codex also uses it to write helpers, test data, and generators without hallucinating.
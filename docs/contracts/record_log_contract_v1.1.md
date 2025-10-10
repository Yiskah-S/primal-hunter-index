# 📜 `contracts/record_log_contract.md` (v1.1)

**Status:** Final
**Updated:** 2025-10-07
**Maintainer:** PHI Data Contracts
**Supersedes:** `record_log_contract_2025-10-05.md` (to be archived)

---

## 📘 Purpose

The `record_log[]` array tracks the **complete change history** of any canon record in PHI.

It answers:

- Who added or changed a fact?
- When was it approved?
- What changed — and why?

This field **lives in the `.meta.json` sidecar** and is **required** for every stable canon ID in `records/`.

---

## 📐 Structure

```json
"record_log": [
  {
    "action": "added",
    "by": "assistant",
    "date": "2025-10-06"
  },
  {
    "action": "approved",
    "by": "user",
    "date": "2025-10-07"
  },
  {
    "action": "edited",
    "by": "user",
    "field": "description",
    "from": "Old value",
    "to": "New value",
    "date": "2025-10-09",
    "notes": "Clarified intent based on new scene evidence"
  }
]
```

---

## 🔍 Field Breakdown

| Field    | Type   | Required? | Notes                                                          |
| -------- | ------ | --------- | -------------------------------------------------------------- |
| `action` | enum   | ✅ yes     | `"added"`, `"edited"`, `"approved"`, `"rejected"`, `"deleted"` |
| `by`     | string | ✅ yes     | `"user"` or `"assistant"` (LLMs must identify themselves)      |
| `date`   | string | ✅ yes     | ISO-8601 date (`YYYY-MM-DD`)                                   |
| `field`  | string | ⛔ no      | Required if `action === "edited"`                              |
| `from`   | string | ⛔ no      | Optional for `edited`; helpful for audits                      |
| `to`     | string | ⛔ no      | Optional for `edited`; include if `from` is present            |
| `notes`  | string | ⛔ no      | Reviewer explanation or assistant rationale                    |

---

## ✅ Required Action Types

| Action       | Description                                            |
| ------------ | ------------------------------------------------------ |
| `"added"`    | First appearance of a record in the repo               |
| `"edited"`   | Change to a specific field or value                    |
| `"approved"` | Human review; unlocks downstream use                   |
| `"rejected"` | Human review; rejected entry must be deleted or moved  |
| `"deleted"`  | Canon entry removed (rare); requires reason in `notes` |

---

## 💡 Why It Matters

- Prevents **silent overwrites**
- Enables **QA tooling** to see who touched what, when, and why
- Supports **Codex-assisted editing** with human verification gates
- Allows **time-travel debugging** and narrative forensics
- Enables future tools like:

  - `show_record_log.py` → "What changed about this skill over time?"
  - `codex_review_assistant.py` → "Flag unapproved edits"

---

## 🔏 Storage Location

- Required for all records in `records/`
- Lives inside the `.meta.json` file **next to** the canonical `record.json`
- Should be the **first field** in `.meta.json` for quick index scan
- `record_log[]` entries MAY reference related provenance by pointer (e.g., event ID, short note), but MUST NOT embed full `source_ref[]` objects. Detailed citations live in timeline events or dedicated provenance sidecars. The log explains *what changed* and *why*; the provenance files provide the *evidence*.


---

## 🧪 Validation Rules

- Every `.meta.json` **must** include a `record_log[]`
- First entry **must** be `{"action": "added", ...}`
- Every edit must include `field`, and preferably `from` / `to`
- Only `"user"` can submit `"approved"` or `"rejected"` entries
- `date` must be `YYYY-MM-DD` (validated by `meta.schema.json`)
- If `certainty: "low"` exists in `source_ref[]`, `record_log[]` must show an approval

---

## ✍️ Examples

### A. Standard review pass

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-06" },
  { "action": "approved", "by": "user", "date": "2025-10-07" }
]
```

---

### B. Complex edit chain

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-03" },
  { "action": "edited", "by": "user", "field": "effects.passive_benefit", "from": null, "to": "Minor HP regen", "date": "2025-10-05" },
  { "action": "approved", "by": "user", "date": "2025-10-06" }
]
```

---

### C. Rejected entry

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-04" },
  { "action": "rejected", "by": "user", "date": "2025-10-05", "notes": "Duplicate of sn.meditation.rank1" }
]
```

---

### D. Codex‑written, pending approval

```json
"record_log": [
  { "action": "added", "by": "assistant", "date": "2025-10-04" }
]
```

Until it’s approved:

- ✅ Visible
- ❌ Not eligible for RAG
- ❌ Not used in QA exports
- ⚠️ May be overwritten without merge protection

---

## 🚫 Anti-Patterns

| Pattern                         | Why It’s Bad                      |
| ------------------------------- | --------------------------------- |
| Missing `"added"` line          | Breaks provenance chain           |
| Edits with no `field` or `to`   | Can't audit what changed          |
| `"approved"` by `"assistant"`   | Codex cannot self-approve canon   |
| `record_log[]` in `record.json` | Must live in `.meta.json` sidecar |
| No log at all                   | 🚨 Will fail meta validator       |

---

## 🔗 Relationship to Other Contracts

| File                                               | Role                                                              |
| -------------------------------------------------- | ----------------------------------------------------------------- |
| [`provenance_contract.md`](provenance_contract.md) | Explains *why* provenance exists and *where* `record_log[]` lives |
| [`source_ref_contract.md`](source_ref_contract.md) | Defines structure and rules of source citation                    |
| `meta.schema.json`                                 | Enforces record_log[], authoring rules, review gating             |

---

## 🧠 Philosophy

> Canon is not a static payload — it’s a living, reviewed, evolving narrative.
> `record_log[]` is how we **show our work**.

It’s how we prove:

- Who added what, and when
- Which facts were manually verified
- What parts of canon are confirmed vs speculative
- Whether Codex content was reviewed or rejected

It turns every record from a black box into a reviewable trail of narrative decisions — exactly what you need to power
aligned generation at scale.

---

### Edge Case Policies

- **Retcons:** When new canon contradicts prior scenes, log a new `record_log` entry with `action: "retconned"` and link
  the new event or scene. Never delete the old data.
- **Conflicts:** If two sources disagree, keep both `source_ref[]` entries; add a reviewer note or `review_decision` to
  mark which interpretation is currently active.
- **Splits/Merges:** When concepts diverge or consolidate, create new IDs and link them using `links[]` (`split_from`,
  `merged_into`).

For enforcement logic, see `tools/validate_provenance.py` — it verifies that each `.meta.json` carries a well-formed
`record_log[]` array per this contract.

---

### Related Docs

- [Provenance Contract](./provenance_contract_v2.0.md)
- [Source Ref Contract](./source_ref_contract_v1.1.md)
- [Provenance Workflow Runbook](../runbooks/provenance_workflow_runbook.md)
- [tools/validate_provenance.py](../tools/validate_provenance.py)

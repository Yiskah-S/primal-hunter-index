# 🏷️ Tagging Pipeline Runbook

**Updated:** 2025-10-07  
**Audience:** Human operators and Codex  
**Maintainer:** PHI Data Engineering  
**Upstream Contracts:** [`contracts/tagging_contract.md`](../contracts/tagging_contract.md) and [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)

---

## 🎯 Purpose

This runbook documents how to safely move tags from **candidate stage** → **canonical registry**, validate them, and ensure they don’t break provenance or schema guardrails.

You’ll use this flow every time new tags are scraped, proposed, or promoted.

---

## 🧱 Folder Structure

| Folder | Role |
|--------|------|
| `tagging/tag_candidates.json` | Staging pool; unverified tags proposed by Codex or human scrapers. |
| `tagging/tag_registry.json` | Canonical approved tags; only these appear in records. |
| `tagging/tag_registry.meta.json` | Sidecar audit log for each approved tag (`record_log[]`, `source_ref[]`, etc.). |
| `schemas/tag_registry.schema.json` | Schema used to validate all tag records. |

---

## 🧩 CLI Overview

### 🔹 `tools/promote_tags.py`

Promotes candidate tags into the canonical registry.  
Always dry-runs first unless `--commit` is provided.

**Usage examples:**
```bash
# Preview promotion for all tags
python3 -m tools.promote_tags --all

# Only tags matching pattern
python3 -m tools.promote_tags --grep "skill\."

# Specific tag IDs
python3 -m tools.promote_tags --ids tag.skills.meditation,tag.entity.jake

# Commit (with backup)
python3 -m tools.promote_tags --all --commit --backup
````

**Flags:**

| Flag                 | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| `--all`              | Promote all candidate tags.                        |
| `--grep <regex>`     | Promote tags matching a regex.                     |
| `--ids <comma list>` | Promote specific IDs.                              |
| `--commit`           | Actually write the registry (otherwise dry-run).   |
| `--backup`           | Write a timestamped `.bak` copy before committing. |

**Guardrails:**

* Schema validated before every write (`schemas/tag_registry.schema.json`).
* Writes via `core/io_safe.write_json_atomic` for safety.
* Mutually exclusive promotion flags.
* Never overwrites canon silently — prompts or backs up instead.

---

### 🔹 `tools/validate_provenance.py`

Runs post-promotion to ensure no tag or record violates provenance guardrails.

**Usage:**

```bash
python3 -m tools.validate_provenance
```

**Checks performed:**

1. Every `timeline.json` event includes a valid `source_ref[]`.
2. Canonical payloads in `records/**.json` do **not** include inline `source_ref[]`.
3. `.meta.json` sidecars carry valid `record_log[]` arrays.
4. Warn if events lack `quote` or `inference` context.
5. Enforce `scene_id` regex `^\d{2}-\d{2}-\d{2}$`.

---

## 🧩 Makefile Hooks

These commands tie the entire flow together:

```make
## Promote selected tags from candidates → registry (dry-run by default)
promote-tags:
	python3 -m tools.promote_tags --grep "$(grep)" $(args)

## Commit a full promotion of all candidates (use with care)
promote-tags-all:
	python3 -m tools.promote_tags --all --commit --backup

## Provenance guardrail check (fails the build on violations)
validate-provenance:
	python3 -m tools.validate_provenance

## Combined validator (lint + schema + provenance)
validate_all: lint
	python3 -m tools.validate_all_metadata
	$(MAKE) validate-provenance
```

---

## 🧠 Promotion Workflow

1. **Dry-run first**

   ```bash
   make promote-tags grep=skill\.
   ```

   Confirm that the printed list matches what you expect.

2. **Review changes**

   * Open `tagging/tag_candidates.json` and confirm fields:

     * `status: "candidate"`
     * `allow_inferred` correctly set
     * `description` and `aliases[]` filled

3. **Commit to registry**

   ```bash
   make promote-tags-all
   ```

4. **Validate**

   ```bash
   make validate-provenance
   ```

5. **Review the results**

   * ✅ No failures = safe to push.
   * ⚠️ Warnings = acceptable if they match inferred tags.
   * ❌ Failures = fix schema/provenance and rerun.

6. **Record the approval**

   * Add `record_log[]` entries in `tag_registry.meta.json` for each promoted tag.
   * Include `source_ref[]` quotes if applicable.

---

## 🧾 Example Workflow Log

```bash
$ make promote-tags grep=skill\.
Dry-run: would add/replace 3 tags:
  - tag.skills.meditation
  - tag.skills.basic_archery
  - tag.skills.spectral_displacement

$ make promote-tags-all
Committed 3 tags → tagging/tag_registry.json

$ make validate-provenance
[OK] All timelines contain source_ref[]
[OK] No inline source_ref in canon payloads
[OK] record_log[] entries valid
```

---

## 🧱 Validation Rules Summary

| Rule                                | Enforced By              | Level   |
| ----------------------------------- | ------------------------ | ------- |
| All tag promotions schema-validated | `promote_tags.py`        | ❌ Fail  |
| Inline source_ref in canon          | `validate_provenance.py` | ❌ Fail  |
| Missing record_log in meta          | `validate_provenance.py` | ❌ Fail  |
| Timeline event missing source_ref   | `validate_provenance.py` | ❌ Fail  |
| Missing quote/inference             | `validate_provenance.py` | ⚠️ Warn |
| Scene ID mismatch                   | `validate_provenance.py` | ❌ Fail  |

---

## 💡 Best Practices

* Never approve `allow_inferred: true` unless the tag represents a **contextual**, not **literal**, trait.
* Use `--grep` patterns to promote tags in controlled batches.
* Keep candidate tags descriptive; don’t over-namespace unless needed.
* Run `pytest -q` after promotion to confirm guardrails and regression tests.
* Update `tag_registry.meta.json` immediately after approval — don’t leave dangling provenance.

---

## 🔗 Related Docs

* [`contracts/tagging_contract.md`](../contracts/tagging_contract.md)
* [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)
* [`contracts/record_log_contract.md`](../contracts/record_log_contract.md)
* [`docs/runbooks/projector_usage.md`](./projector_usage.md)
* [`docs/design/pipeline_flow.md`](../design/pipeline_flow.md)

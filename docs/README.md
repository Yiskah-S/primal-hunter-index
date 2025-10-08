# Documentation Map

This index helps you locate authoritative repo docs, understand their intent, and keep naming/metadata conventions consistent. Treat it as the single source of truth for documentation hygiene.

---

## Directory Roles

`contracts/` — Normative specifications that the codebase and schemas must follow.
- Versioned filenames are required (`*_contract_vX.Y.md`).

`design/` — System narratives, diagrams, and long-form reasoning.
- Use `Status: Informational` unless the doc is still evolving.

`adr/` — Architectural Decision Records.
- Immutable snapshots; never rewrite history.

`runbooks/` — Operational guides for day-to-day workflows.
- Update as processes change; keep examples current.

`archive/` — Deprecated material retained for context.
- Do not link from living docs unless called out as history.

---

## Required Front Matter

All docs start with a small metadata block to keep status obvious during quick skims.

````markdown
Title: Tagging Contract (PHI)
Status: Final (v0.3)
Updated: 2025-10-06
Supersedes: Tagging Contract v0.2 (2025-10-05)
````

ADR headers stick to the classic pattern:

````markdown
ADR-0001: Split status vs tag_role for tags
Date: 2025-10-06
Status: Accepted
Context: …
Decision: …
Consequences: …
````

Runbooks and designs generally use `Status: Living` while in active use, and shift to `Status: Deprecated` when archived.

---

## Quick Navigation

**Contracts** (enforced rules):

- `contracts/skills_contract_v1.0.md`
- `contracts/provenance_contract_v2.0.md`
- `contracts/record_log_contract_v1.1.md`
- `contracts/id_contract_v1.1.md`
- `contracts/tagging_contract_v0.4.md`
- Planned: `contracts/timeline_contract_v1.0.md`

**Design references** (why decisions make sense):

- `design/skills_overview_design.md`
- `design/storage_layout_design.md`
- `design/pipeline_flow_design.md`
- `design/graph_links_design.md`

**Runbooks** (how to operate the system):

- `runbooks/skills_entry_runbook.md`
- `runbooks/skills_structure_runbook.md`
- `runbooks/provenance_workflow_runbook.md`
- `runbooks/projector_usage_runbook.md`
- `runbooks/tagging_process_runbook.md`

**ADRs** (history of change):

- `adr/ADR-0001.md` — Split `status` vs `tag_role` for tags (2025-10-06).  
- `adr/ADR-0002.md` — Reserved for the next accepted decision.

Other helpful material: the repo root `README.md` for onboarding, plus the `docs/design/pattern_grounded_hallucination.md` exploration of retrieval guardrails.

---

## Adding or Updating Docs

1. Pick the correct directory using the table above.  
2. Follow the naming pattern: `<category>_<topic>_<doc-type>[_vX.Y].md`.  
3. Add/update the metadata block with `Title`, `Status`, `Updated`, and `Supersedes` when relevant.  
4. Link back to related docs (contracts to runbooks, runbooks to tooling).  
5. Append a bullet or table entry in this index; nothing ships without appearing here.  
6. Run `markdownlint` (or the repo lint target) before opening a PR.

---

## Maintenance Guardrails

- Contracts require an explicit version suffix and changelog entry if they supersede older material.  
- Designs and runbooks should call out any dependencies on tooling or scripts so changes stay discoverable.  
- Archive stale docs rather than deleting them; add a short note at the top explaining why they moved.  
- Treat this index as living documentation—update it whenever you touch docs elsewhere.  
- When schema or tooling introduces a breaking change, capture it in both the relevant contract and an ADR.

---

*Last updated: 2025-10-08*

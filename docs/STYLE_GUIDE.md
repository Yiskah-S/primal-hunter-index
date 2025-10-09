# Documentation Style Guide (PHI)

**Status:** Living  
**Updated:** 2025-10-08  
**Audience:** Anyone writing or reviewing repo docs  
**Purpose:** Keep formatting consistent across contracts, runbooks, and design notes.

---

## Quick Reference

| Topic | Rule | Example |
| --- | --- | --- |
| Front matter | Always include `Title`, `Status`, `Updated`, and related links. | See metadata templates below |
| Headings | Use sentence case; prefix numbered sections when the doc is procedural. | `## 1. Provenance Basics` |
| Lists | Prefer `-` for unordered items; use `1.` for ordered lists. | `- canonical fact` |
| Links | Prefer relative markdown links. | `[skills_contract](contracts/skills_contract_v1.0.md)` |
| Callouts | Use `>` blockquote syntax sparingly for quotes or inline tips. | `> Reminder:` |
| Code blocks | Add language hints when possible. | ```json {...}``` |
| Footers | End with `Related Docs` + `Last updated`. | See footer template |

---

## 1. Front Matter Templates

Use these at the top of every doc (adjust fields as needed).

```markdown
Title: Tagging Contract (PHI)
Status: Final (v0.4)
Updated: 2025-10-08
Linked Schemas: schemas/shared/tags.schema.json
Linked Runbooks: docs/runbooks/tagging_process_runbook.md
```

For runbooks and design notes, include audience or source if useful:

```markdown
Title: Skill Entry Runbook (PHI)
Status: Living
Updated: 2025-10-08
Audience: Human data entry + Codex automation
Linked Contract: docs/contracts/skills_contract_v1.0.md
```

After the metadata block, add a horizontal rule (`---`).

---

## 2. Headings & Sections

- Main title uses `#` followed by the doc name.
- Subsequent headings use `##`. Indent further detail with `###` only when necessary.
- Numbered headings (e.g., `## 1.`) are encouraged for procedural guides.
- Keep heading text in sentence case (capitalize only the first word and proper nouns).

---

## 3. Lists & Tables

- Use `-` for unordered lists across the repo. Avoid mixing `*` and `-`.
- Ordered lists should use `1.` on each line—Markdown will render correct numbering.
- When summarizing multiple docs or data points, prefer tables so status/notes stay aligned.

Example table row:

```markdown
| [skills_contract_v1.0.md](contracts/skills_contract_v1.0.md) | Final | Skill family & node rules |
```

---

## 4. Links & Cross-References

- Always prefer relative links within the repo (`[Runbook](../runbooks/provenance_workflow_runbook.md)`).
- For tool references, point to the actual script under `tools/`.
- When adding a new doc, update `docs/README.md` and the `Related Docs` section of peers.

---

## 5. Callouts, Quotes, and Notes

- Use blockquotes (`>`) for brief quotes or emphasis only.
- Avoid Markdown html or custom admonition syntax—keep it plain for portability.
- Inline code backticks (`` `like this` ``) are preferred for IDs, file names, or field keys.

---

## 6. Code Blocks & Samples

- Always specify a language hint when possible (` ```json`, ` ```bash`).
- Keep samples minimal and reflect actual schema/tool usage.
- For JSON snippets, honor our indentation (tabs) and include only the relevant keys.

---

## 7. Footer Template

Every doc should end with:

```markdown
---

### Related Docs

- [Example Contract](../contracts/example_contract.md)
- [Example Runbook](../runbooks/example_runbook.md)

---

**Last updated:** 2025-10-08
```

Replace the date and links appropriately. `Related Docs` should list 3–5 directly relevant files.

---

## 8. Review Checklist

Before committing doc changes, confirm:

1. Front matter matches the template and includes current `Status`/`Updated` dates.
2. Headings use consistent casing; numbered sections when helpful.
3. Lists use `-` (unordered) or `1.` (ordered) exclusively.
4. Links point to relative paths and render in Markdown previews.
5. Footer includes `Related Docs` and `Last updated`.
6. Lint passes (`npx markdownlint-cli ...` or `make lint`).

Keeping to these guidelines keeps Codex, ChatGPT, and humans aligned when writing or reviewing documentation.

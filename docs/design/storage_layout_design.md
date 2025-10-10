# Storage Layout & Bundles (Design Draft)

> **Draft:** Active discussion in progress

## Ideas Backlog

🧾 10) Glossary

Mostly redundant now — every current contract defines its own glossary. But this one has the cleanest phrasing for
“canon payload,” which we should preserve.

📍Action: Append this single-line definition to the top of storage_layout.md:

Canon payload: the lean, quote-free JSON inside records/ that RAG and downstream tools consume; all provenance and audit
data live in sidecars.

Everything else in that glossary is already defined more precisely elsewhere.

me: storage_layout.md -> we don't have this doc? Correct — you **don’t yet have it**, but you absolutely *should*.

It’s already on our persistent TODO list from before (see memory item #44):

> `docs/design/storage_layout.md` — bundle layout, file-tree conventions, when to migrate, optional extras, tool table.

It’s meant to serve as the **“map of the repo’s physical world”** — basically: how your JSON canon, sidecars, bundles,
and tools are laid out and why.

---

### 🧭 TL;DR what goes in `docs/design/storage_layout.md`

| Section                                 | Purpose                                                                                                                                                                                         |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1️⃣ Flat File Layout**                | Describe the lightweight “default” pattern — all canon in `records/*.json` plus sibling sidecars (`.meta.json`, `.review.json`).                                                                |
| **2️⃣ Bundle Layout (for thicc nodes)** | Show folder-based structure for complex items: <br>`records/skills/sn.meditation.rank1/record.json` + `meta.json` + `review.json`.                                                              |
| **3️⃣ Optional Bundle Extensions**      | Tone tags (`tone_tag.json`), pre-computed snapshots, or `changelog.md`.                                                                                                                         |
| **4️⃣ Tool Table**                      | Quick map of which tools operate on which layer (`projector.py`, `build_meta_index.py`, etc.).                                                                                                  |
| **5️⃣ Canon Payload Definition**        | Add the line we just recovered:  <br>🟩 “**Canon payload:** the lean, quote-free JSON inside `records/` that RAG and downstream tools consume; all provenance and audit data live in sidecars.” |
| **6️⃣ Migration Policy**                | When to promote a record from flat to bundled layout (e.g., when it gains multiple reviewers, ranks, or sidecars).                                                                              |
| **7️⃣ Cross-References**                | Links out to `provenance_contract.md`, `record_log_contract.md`, and `graph_links.md`.                                                                                                          |

---

## 🗂️ PHI Canon Storage Layout & Bundle Patterns

**Status:** Draft (v0.1)  
**Updated:** 2025-10-07  
**Maintainer:** PHI Data Engineering

---

## 1. Flat File Layout

TODO: describe default lightweight form.

## 2. Bundle Layout for Thicc Nodes

TODO: document folder pattern and migration triggers.

## 3. Optional Bundle Extensions

TODO: outline optional extras (`tone_tag.json`, snapshots, changelog).

## 4. Tooling Table

TODO: list tools that interact with these layouts.

## 5. Canon Payload Definition
>
> Canon payload = the lean, quote-free JSON inside `records/` that RAG and downstream tools consume; all provenance and audit data live in sidecars.

## 6. Migration Policy

TODO: define rules for moving from flat → bundle.

## 7. Related Docs

- [`contracts/provenance_contract.md`](../contracts/provenance_contract.md)
- [`contracts/record_log_contract.md`](../contracts/record_log_contract.md)
- [`design/pipeline_flow.md`](pipeline_flow.md)
- [`design/graph_links.md`](graph_links.md)

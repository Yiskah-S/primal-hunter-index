# Docs Map


File roles
contracts/ = the source of truth; schema and code must follow.

designs/ = explanatory docs, diagrams, system narratives (stable but non‑normative).

adr/ = immutable decisions with context & alternatives (short, dated).

runbooks/ = step‑by‑step ops/playbooks (how to promote, approve, validate).

archive/ = kept for history; not part of the “living” set.

Headers to add (keep doc status obvious)

At the top of every doc, include:

Title: Tagging Contract (PHI)
Status: Final (v0.3)
Updated: 2025‑10‑06
Supersedes: Tagging Contract v0.2 (2025‑10‑05)


For ADRs:

ADR-0001: Split status vs tag_role for tags
Date: 2025‑10‑06
Status: Accepted
Context: …
Decision: …
Consequences: …


For designs/runbooks, use Status: Informational or Status: Living.
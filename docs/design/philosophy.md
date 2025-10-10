# Project Philosophy: Why This Isn't Just a Wiki

📁 File: `docs/design/philosophy.md` 📅 Last updated: 2025-10-07

---

## What This Project *Really* Is

This project is a structured metadata engine for *The Primal Hunter* universe — but it's not a wiki. It's a
**provenance-aware, schema-driven, tone-tagged narrative compiler** designed to enable:

- Canon-faithful event tracking across characters, scenes, and timelines  
- Rich tagging of narrative tone, system mechanics, and power progression  
- Hallucinated content (fanfic, alternate POV chapters) that remains **faithful to canon and vibe**  
- A future-ready foundation for fine-tuned generation or RAG-based storytelling tools

At its heart, this project is a **training-ground for narrative scaffolding systems** — where facts, tone, and
timeline form the rails that keep AI‑assisted fiction *in universe*.

---

## Why We're Not Just Building a Wiki

If this were a wiki, we’d only need two things:

- A list of known facts
- A way to query them

But a wiki can’t:

- Preserve scene‑by‑scene tone and narrative function  
- Guide AI output to stay in‑character, in‑universe, and in‑style  
- Prevent hallucinated skills, timelines, or story arcs  
- Distinguish **facts** from **inferred narrative assumptions**

That’s what this system is designed to do — and why it's **intentionally overbuilt**. We aren't just indexing
PH canon. We're teaching systems how to **write like they belong in it**.

---

## RAG, Tone, and the Narrative Compiler

This system is designed for **retrieval-augmented generation (RAG)** with **narrative alignment**:

- Timeline-based facts serve as the **grounding layer**  
- `tag_registry.json` and `tone_tag[]` inject style, cadence, and mood  
- `source_ref[]`, `quote`, and `inference` metadata differentiate what's known vs. assumed  
- Future tools (LLMs, prompts, generators) can combine these signals to produce:
  - ⚖️ Canon-consistent facts  
  - 🧠 Tone-faithful narrative  
  - 🎯 Story arcs that follow established rules without directly copying them

It’s not just “don’t hallucinate.” It’s “hallucinate responsibly — with source citations, tone, and in-
universe constraints.”

---

## Provenance Isn’t Just for Facts — It’s for Alignment

In this system, provenance tracks:

- **What** a fact is
- **Where** it came from
- **How sure** we are about it
- Whether it’s a **direct quote** or **inference**
- And **who** added or confirmed it

This isn't trivia. It's narrative control.

Provenance makes it possible to:

- Weight different sources by certainty  
- Flag inferred content during generation  
- Reconstruct the narrative state at any point in time  
- Distill tone + logic from canon to guide future fiction

Without provenance, any hallucinated output is just fanon. With it, hallucinated output can become *canon-
consistent fiction*.

---

## Resume Signal: Why This Matters

This project demonstrates the architecture behind:

- 🔧 Schema-first, contract-driven design
- 🧱 Modular records + metadata separation
- 🧠 Tone-stable, LLM-ready tagging pipelines
- 🧾 Quote-backed provenance modeling
- ⚙️ Validators, review logs, and QA enforcement
- 🎯 Hallucination mitigation + narrative alignment via metadata

It doesn’t just store Zogarth’s universe — it teaches the machine how to *write in it without breaking it*.

For a deeper dive into the reusable pattern behind this architecture, see:

📄 [`pattern_grounded_hallucination.md`](docs/design/pattern_grounded_hallucination.md)

---

## Disclaimer

This is a personal, non-commercial fan project created with admiration for *The Primal Hunter* by Zogarth.

All original content and intellectual property belong to the author. This project is intended for learning,
research, and transformative exploration of the PH universe through structured metadata and AI tooling. No
chapter content is redistributed or monetized. Any future public-facing content will be subject to author
permission and attribution.

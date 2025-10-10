# Tag Registry Design

Define a controlled vocabulary that steers generation (tone, style, scene intent, mechanics) and anchors retrieval. Tags must change how the model writes; if a tag doesn’t imply a concrete instruction to the generator, it doesn’t exist in v1.

---

## 1) Scope & Principles

- **Control-first:** Tags are levers, not mere labels. Every tag comes with an operational instruction (what the generator should do).
- **Four primary buckets** (v1):
  - `narrative_style` — narrator’s voice/structure.
  - `character_tone` — POV voice/attitude.
  - `scene_function` — story purpose of the scene.
  - `system_mechanic` — explicit mechanics referenced.
- **Optional v1 buckets:** `power_scaling`, `lore_topic` (use sparingly).
- **Parsimony:** Better to be roughly right with 36 good tags than precisely wrong with 300.
- **No overlaps:** Each tag belongs to exactly one category.
- **Cardinality rules:** Limit how many tags of each category can apply per scene (see §6).
- **Lifecycle:** `candidate → approved → deprecated` with gates (see §7).
- **Dotted scenes:** Scene IDs are `BB.CC.SS` everywhere (keeps the ecosystem coherent).
- **Registry is code:** The JSON registry is the single source of truth; the docs page is generated.

---

## 2) Data Model

**Registry file:** `tag_registry.json`

**Object shape (per tag)**

```json
{
  "id": "dry_humor",
  "category": "narrative_style",
  "label": "Dry humor",
  "status": "approved",
  "allow_inferred": true,
  "scope": ["scene","line"],

  "definition": "Understated irony; humor by contrast, not punchline.",
  "use_when": [
    "Deadpan observations",
    "Absurdity noted without lampshading"
  ],
  "not_when": [
    "Mean-spirited sarcasm (use 'sardonic')",
    "Slapstick comedy"
  ],
  "generator_instruction": "Insert understated mismatches; avoid overt emphasis or exclamation.",
  "examples": [
    {"scene_id":"01.02.01","line":1,"excerpt":"The air flickers, overlaid by a pale interface only he can see."}
  ],
  "aliases": ["deadpan_humor"],
  "notes": "If paired with 'sardonic', keep cruelty low."
}
```

**Field glossary**

- `id` — stable machine key (`^[a-z0-9_\.]+$`)
- `category` — one of the enumerated buckets
- `label` — human title
- `status` — `approved | candidate | deprecated`
- `allow_inferred` — if tag can be applied without explicit quote (styles/tones usually yes; mechanics usually no)
- `scope` — where it applies: `scene`, `line`, and/or `character_default`
- `definition` / `use_when` / `not_when` — annotator guidance
- `generator_instruction` — single sentence that changes model output
- `examples` — optional list of citations (scene/line/excerpt)
- `aliases` — non-canonical synonyms (for search), not separate tags
- `notes` — freeform

---

## 3) Schema (authoritative; keep in `schemas/tag_registry.schema.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tag_registry.schema.json",
  "type": "object",
  "required": ["version","tags"],
  "properties": {
    "version": {"type":"string"},
    "tags": {
      "type":"array",
      "items": {
        "type":"object",
        "required": ["id","category","label","status","allow_inferred","scope","definition","generator_instruction"],
        "additionalProperties": false,
        "properties": {
          "id": {"type":"string","pattern":"^[a-z0-9_\\.]+$"},
          "category": {
            "type":"string",
            "enum":["narrative_style","character_tone","scene_function","system_mechanic","power_scaling","lore_topic"]
          },
          "label": {"type":"string"},
          "status": {"type":"string","enum":["approved","candidate","deprecated"]},
          "allow_inferred": {"type":"boolean"},
          "scope": {"type":"array","items":{"type":"string","enum":["scene","line","character_default"]}},
          "definition": {"type":"string"},
          "use_when": {"type":"array","items":{"type":"string"}},
          "not_when": {"type":"array","items":{"type":"string"}},
          "generator_instruction": {"type":"string"},
          "examples": {
            "type":"array",
            "items": {
              "type":"object",
              "required": ["scene_id"],
              "properties": {
                "scene_id":{"type":"string","pattern":"^\\d{2}\\.\\d{2}\\.\\d{2}$"},
                "line":{"type":"integer","minimum":1},
                "excerpt":{"type":"string","maxLength":320}
              },
              "additionalProperties": false
            }
          },
          "aliases": {"type":"array","items":{"type":"string","pattern":"^[a-z0-9_\\.]+$"}},
          "notes": {"type":"string"}
        }
      }
    }
  }
}
```

---

## 4) Methodology to create (and limit) the seed list

1. **Start from control needs** (what you steer during generation): rule clarity, POV voice, scene intent, mechanics.
2. **Pilot on 10–15 scenes** across different modes (tutorial, fight, reveal, aftermath).
3. **Record missing tags as candidates**, but only keep those that pass the **Do/Describe test**:
   - *Describe-only?* (taxonomy trivia) → reject or fold into another tag.
   - *Do-tag?* (implies a clear instruction) → keep.
4. **Cap v1 sizes** (≈ 8–10 narrative_style, 6–8 character_tone, 10–12 scene_function, 10–12 system_mechanic).
5. **Spec cards** for each kept tag (the fields above).
6. **Cardinality** (see §6) — encode category-level limits for annotators and validators.
7. **Lifecycle** (see §7) — drafts can use `candidate`, but exports hard-fail anything not `approved`.

---

## 5) Integration: how tags affect the pipeline

- **Authoring / Annotation**
  - Scene files (`scene_index/**.json`) hold `tone_tag[]` and `scene_function[]`; lines may carry `system_mechanic[]`.
  - Character defaults live in `canon/characters/**/profile.json` as `tone_profile` (not tags), merged at runtime.
- **Projector**
  - Outputs a `recent_tone` window: `{tone_tag, scene_function}` from the last K scenes, merged with character defaults.
- **Export bundle**
  - Spans with `narrative_style|character_tone` get higher `weights.tone`.
  - Spans with `system_mechanic` get higher `weights.mechanics`.
  - Non-approved tags are excluded (or down-weighted in dev exports).
- **Validators**
  - `validate_tags.py` resolves every tag to the registry, respects `status`, checks cardinality per category, and enforces `allow_inferred` (e.g., `system_mechanic` requires explicit textual evidence).

---

## 6) Cardinality & scope rules (encode in validator config)

- `narrative_style`: ≤3 per scene; order by importance (primary, secondary, tertiary).
- `character_tone`: ≤2 per scene (dominant, accent). Character default is not counted here; it merges at runtime.
- `scene_function`: 1–2 per scene.
- `system_mechanic`: line-level preferred; scene-level allowed when pervasive.

---

## 7) Lifecycle & governance

- **States:** `candidate → approved → deprecated`.
- **Drafts:** may use `candidate` (lint warns).
- **Export/training:** hard-fail any tag not `approved`.
- **Promotion criteria:** appears in ≥2–5% of annotated scenes, passes Do/Describe, distinct from existing tags, and improves generation control in A/B tests.
- **Deprecation:** if co-occurrence with another tag >80% for a month, propose merge; if <1% usage for a month, propose deprecate. Record `notes` and `aliases`.

---

## 8) Annotator guide (1-minute spec card = these fields)

- **Definition:** one sentence.
- **Use when:** 2–3 bullets.
- **Not when:** 1–2 bullets (common confusions).
- **Generator instruction:** one sentence that changes prose.
- **Example:** one 320-char excerpt (optional but great).

These are exactly the fields in the registry; the docs page is generated from them.

---

## 9) Risks & mitigations

- **Tag inflation:** people add near-synonyms.  
  **Mitigation:** weekly triage; enforce A/B generation impact before approval.
- **Over-tagging:** annotators carpet-bomb scenes.  
  **Mitigation:** cardinality limits plus linter warnings.
- **Ambiguous tags:** “kinda funny” noise.  
  **Mitigation:** apply the Do/Describe test; sharpen the generator instruction.
- **Drift between registry and docs:**  
  **Mitigation:** generate docs from the registry; add a CI check.

---

## 10) FAQ

- **Can a tag belong to two categories?** No. Pick one or split into distinct tags.
- **Can we tag a whole chapter?** Use scene-level tags; chapters are collections of scenes.
- **What about multi-POV scenes?** Tag by the current POV; switch when POV switches.

---

## Draft design notes & reminders

- Cardinality enforcement in UI: bake the per-category limits into your tagging UI so annotators can’t go wild.
- A/B generation checks for new tags: a tag isn’t approved until flipping it measurably alters generated prose in the intended way.
- Alias policy: prefer aliases over new tags for synonyms; merge if co-occurrence >80%.
- Telemetry hooks: track % of scenes using each tag and pairwise co-occurrence. This drives governance decisions.
- Separation of defaults vs tags: keep character defaults in `profile.json`; don’t tag every scene with the same tone. Use scene tags for changes and for steering.
- `allow_inferred` discipline: for `system_mechanic`, keep `allow_inferred: false` so we never teach the model rules that weren’t explicitly shown. Styles/tones can be inferred.
- Export-time strictness: drafts can be loose; exports hard-fail on non-approved tags. This is where alignment lives.
- Docs generation: add a tiny `tools/render_tag_docs.py` that turns the registry into `docs/reference/tags.md` with sections per category and spec cards, so there’s no drift.

### Q1) “Jake is always a bit blasé.” Should that live as tags or a character trait?

Both — with clear precedence and different jobs.

Character profile (default tone) = long‑term persona. Store in canon/characters/<id>/profile.json as a stable vector of tone weights, e.g.:

```json
{
  "id": "jake",
  "tone_profile": {
    "dominant": ["engineer_mindset"],
    "accent": ["sardonic"],
    "weights": {
      "engineer_mindset": 0.8,
      "sardonic": 0.4
    }
  }
}
```


Why: You don’t want to re‑tag every scene to say Jake is Jake.

Scene‑level character_tone tags = momentary steering and deviations. Tag the scenes when Jake isn’t blasé (panic, grief) or when you want the generator to push the accent harder.

Projector rule: scene_tone = merge(character.tone_profile, scene.character_tone) where scene tags override/boost for that scene only. This gives you efficient defaults and explicit control when things change.

### Q2) “Mini spec cards” — document page, registry data, or both?

Both, from one source of truth (the registry).

Put the spec card fields inside the registry so tools can use them (definitions, “when to use,” “not for,” and the one‑line instruction to the generator).

Auto‑generate a docs page from the registry on build, so humans get a readable catalogue that never drifts.

Concretely: add fields like definition, use_when, not_when, generator_instruction, allow_inferred, scope to each tag entry. Use a tiny script to render these into a Markdown reference.

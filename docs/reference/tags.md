# Tag Registry Reference

_Source: `tagging/tag_registry.seed.json`_

## Narrative Style

### Clinical report (`clinical_report`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, line
- **Definition:** Logbook style; measurements and outcomes.
- **Use when:**
  - Experiments
  - Cooldown tracking
  - Stat deltas
- **Not when:**
  - Emotional introspection
- **Generator instruction:** Tabulate variables→result; use neutral lexicon.

### Dialogue-heavy (`dialogue_heavy`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Scene advances primarily via dialogue.
- **Use when:**
  - Negotiations
  - Interrogations
  - Team planning
- **Not when:**
  - Solitary internal monologue
- **Generator instruction:** Maximize spoken lines; trim narration to beats and cues.

### Dry humor (`dry_humor`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, line
- **Definition:** Understated irony; humor by contrast, not punchline.
- **Use when:**
  - Deadpan observations
  - Noting absurdity without emphasis
- **Not when:**
  - Mean sarcasm (use 'sardonic')
  - Slapstick
- **Generator instruction:** Insert understated mismatch per paragraph; avoid exclamation or lampshading.
- **Aliases:** deadpan_humor

### Introspective lens (`introspective_lens`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Interior thought dominates; reflection and self-assessment.
- **Use when:**
  - Aftermaths
  - Decisions
  - Guilt/doubt
- **Not when:**
  - External action focus
- **Generator instruction:** Weight internal appraisal; reduce external detail density.

### Mythic elevation (`mythic_elevation`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Elevated, heroic register; grand metaphor.
- **Use when:**
  - Legendary feats
  - Threshold moments
- **Not when:**
  - Routine fights or tutorials
- **Generator instruction:** Broaden imagery; longer periodic sentences; 1–2 evocative metaphors per page.

### Pulp grit (`pulp_grit`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Kinetic action with tactile detail and pace.
- **Use when:**
  - Fights
  - Dangerous traversal
- **Not when:**
  - Mythic elevation
- **Generator instruction:** Use short sentences, concrete verbs, sensory detail; low metaphor density.

### Recursive logic (`recursive_logic`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Stepwise reasoning where conclusions feed the next step.
- **Use when:**
  - Planning
  - Puzzle solving
  - Meta-reasoning
- **Not when:**
  - Vibes-only monologue
- **Generator instruction:** Chain short logical clauses with clear therefore/so pivots.

### Rule explainer (`rule_explainer`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, line
- **Definition:** Expository tone that states or derives a system rule.
- **Use when:**
  - Tutorials
  - Mechanic summaries
  - Cause→effect statements
- **Not when:**
  - Character opinions about rules (use character_tone)
- **Generator instruction:** Prefer declarative sentences; show premise→consequence; include one explicit rule.

### Tight suspense (`suspense_tight`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Withheld info, short beats, rising uncertainty.
- **Use when:**
  - Searches
  - Stealth
  - Unknowns
- **Not when:**
  - Open exposition
- **Generator instruction:** Shorten sentences; end some lines mid-thought; delay reveals.

## Character Tone

### Compassionate healer (`compassionate_healer`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Care-first, triage thinking.
- **Use when:**
  - Medical/aid scenes
  - Moral harm decisions
- **Not when:**
  - Ruthless min-max
- **Generator instruction:** Prioritize safety and dignity in choices.

### Earnest (`earnest`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Sincere, straightforward, values-forward.
- **Use when:**
  - Helping
  - Teaching
  - Pledges
- **Not when:**
  - Cynical digs
- **Generator instruction:** Avoid irony; emphasize intent and care.

### Engineer mindset (`engineer_mindset`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Operational thinking: variables and procedures.
- **Use when:**
  - Testing skills
  - Planning
  - Evaluation
- **Not when:**
  - Gut-only decisions
- **Generator instruction:** Translate observations to hypotheses; track results.

### Impulsive (`impulsive`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Action before full analysis.
- **Use when:**
  - Snap decisions
  - Fights
  - Surprises
- **Not when:**
  - Methodical planning
- **Generator instruction:** Use reaction-first lines; justify after the fact.

### Paranoid planner (`paranoid_planner`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Redundancy and threat modeling.
- **Use when:**
  - Heists
  - Dangerous missions
- **Not when:**
  - Relaxed banter
- **Generator instruction:** Enumerate risks; add fallback plans.

### Ruthless pragmatist (`ruthless_pragmatist`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Outcome over niceties.
- **Use when:**
  - Survival
  - High stakes
- **Not when:**
  - Sentimental beats
- **Generator instruction:** Choose efficient, if harsh, options; minimal remorse text.

### Sardonic (`sardonic`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Wry, slightly biting commentary.
- **Use when:**
  - Coping through humor
  - Undercutting pomp
- **Not when:**
  - Earnest uplift
- **Generator instruction:** Add dry asides that deflate pretension; keep cruelty low.

### Stoic (`stoic`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, character_default
- **Definition:** Controlled affect; emotion acknowledged but contained.
- **Use when:**
  - Pain
  - Loss
  - Duty
- **Not when:**
  - Outbursts
- **Generator instruction:** State facts and choices; minimize emotive adjectives.

## Scene Function

### Aftermath (`aftermath`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Consequences processed post-conflict.
- **Use when:**
  - Post-battle
  - Post-reveal
- **Not when:**
  - Setup
- **Generator instruction:** Summarize wounds, resources, and social fallout.

### Class choice (`class_choice`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** scene
- **Definition:** A class is selected or rejected.
- **Use when:**
  - System UI offers class
- **Not when:**
  - Pure speculation
- **Generator instruction:** Show options, criteria, and decision outcome.

### Confrontation (`confrontation`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Direct opposition escalates.
- **Use when:**
  - Rivals collide
- **Not when:**
  - Subtle tension
- **Generator instruction:** Escalate pressure; force a decision or cost.

### Exposition (`exposition`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Conveys setting, context, or background knowledge.
- **Use when:**
  - Readers need facts or orientation
- **Not when:**
  - Action advances plot more than info
- **Generator instruction:** State necessary facts plainly; keep causal links explicit.

### Foreshadowing (`foreshadowing`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Hints future events or twists.
- **Use when:**
  - Planting setups
- **Not when:**
  - Explicit reveals
- **Generator instruction:** Introduce subtle cues tied to future payoffs; avoid resolution.

### Investigation (`investigation`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Clue gathering and hypothesis testing.
- **Use when:**
  - Mysteries
  - Unknown systems
- **Not when:**
  - Action-resolved scenes
- **Generator instruction:** Pose explicit hypotheses; update them with each clue.

### Negotiation (`negotiation`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Conflict resolved via dialogue terms.
- **Use when:**
  - Bargains
  - Allies/enemies talk terms
- **Not when:**
  - Pure combat
- **Generator instruction:** Clarify stakes, BATNA, and concessions.

### Power scaling moment (`power_scaling_moment`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Demonstrates a capability increase or threshold.
- **Use when:**
  - New skill tier
  - After training
- **Not when:**
  - No before/after delta
- **Generator instruction:** Surface before/after capability delta and its consequences.

### Stat gain reveal (`stat_gain_reveal`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Reveals a stat increase or new metric.
- **Use when:**
  - System feedback scenes
- **Not when:**
  - Ambiguous changes
- **Generator instruction:** Name the stat, the increment, and the trigger.

### Training montage (`training_montage`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Condensed practice across attempts.
- **Use when:**
  - Repeated drills
- **Not when:**
  - Single attempt
- **Generator instruction:** Aggregate attempts with outcome trend; minimal filler.

### Tutorial prompt (`tutorial_prompt`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** In-world walkthrough for a mechanic.
- **Use when:**
  - First encounter with an interface
- **Not when:**
  - Generic exposition
- **Generator instruction:** Enumerate steps with expected inputs/outputs.

### Worldbuilding vignette (`worldbuilding_vignette`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Flavor detail of setting or culture.
- **Use when:**
  - Setting matters
- **Not when:**
  - Mechanics focus
- **Generator instruction:** Highlight 1–2 vivid details tied to lore.

## System Mechanic

### Class selection UI (`class_selection_ui`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** Visible interface for class selection.
- **Use when:**
  - UI appears
- **Not when:**
  - Off-screen choice
- **Generator instruction:** Show menu items or selection affordances.

### Cooldown display (`cooldown_display`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** Visible cooldown timer/number.
- **Use when:**
  - Numbers on screen
- **Not when:**
  - Feeling that it 'takes a while'
- **Generator instruction:** Include explicit numeric cooldowns.

### Crafting recipe (`crafting_recipe`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** Recipe listing components and outputs.
- **Use when:**
  - Recipe text visible
- **Not when:**
  - Guesswork
- **Generator instruction:** List components and output, verbatim if possible.

### Damage formula hint (`damage_formula_hint`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** Direct hint of formulaic damage scaling.
- **Use when:**
  - Numbers or formula cues appear
- **Not when:**
  - Subjective 'hits harder'
- **Generator instruction:** State variables and proportionality if visible.

### Perk unlock (`perk_unlock`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** System grants a perk/feature.
- **Use when:**
  - Unlock text shown
- **Not when:**
  - Unclear gain
- **Generator instruction:** Name the perk and the unlock condition.

### Quest prompt (`quest_prompt`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** System offers an objective with rewards.
- **Use when:**
  - Prompt text visible
- **Not when:**
  - Organic goals
- **Generator instruction:** Show objective and reward line.

### Resistance interaction (`resistance_interaction`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** Element/resistance rules shown by effect changes.
- **Use when:**
  - Explicit resistance result
- **Not when:**
  - Rumored interactions
- **Generator instruction:** Name elements and observed effect shift.

### Resource pool change (`resource_pool_change`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** Numerical change to mana/stamina/etc.
- **Use when:**
  - Resource value shown
- **Not when:**
  - Vague fatigue
- **Generator instruction:** State pool name and delta.

### Skill description (`skill_description`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line
- **Definition:** Explicit text describing a skill.
- **Use when:**
  - System displays description
- **Not when:**
  - Player speculation
- **Generator instruction:** Include the canonical phrasing of the description if available.

### Stat allocation (`stat_allocation`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** Assigning points to stats.
- **Use when:**
  - Allocation UI or confirmed action
- **Not when:**
  - Speculative planning
- **Generator instruction:** List stat, amount, and immediate effect if shown.

### Tier threshold (`tier_threshold`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** Crossing a tier boundary with systemic effects.
- **Use when:**
  - Threshold text present or numeric boundary hit
- **Not when:**
  - Vague power creep
- **Generator instruction:** Name threshold, pre/post effects, and triggering metric.

### Title award (`title_award`)

- **Status:** approved
- **Allow inferred:** no
- **Scope:** line, scene
- **Definition:** System confers a title.
- **Use when:**
  - Award text present
- **Not when:**
  - Rumors of a title
- **Generator instruction:** Show award text and triggering condition.

## Power Scaling

### Grade progression (`power_scaling.grade_progression`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene
- **Definition:** Skill/class grade increases along defined ladder.
- **Use when:**
  - Grade label changes upward
- **Not when:**
  - Temporary buff
- **Generator instruction:** State old→new grade and trigger.

## Lore Topic

### System terminology (`lore_topic.system_terminology`)

- **Status:** approved
- **Allow inferred:** yes
- **Scope:** scene, line
- **Definition:** Terminology that explains System semantics.
- **Use when:**
  - Terms are defined or clarified
- **Not when:**
  - Offhand slang
- **Generator instruction:** Present term and definition succinctly.

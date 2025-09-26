# Primal Hunter Scene Index & Timeline Project

This project tracks character progression, scene-level metadata, and world events for "The Primal Hunter" using modular JSON files and GPT-based scene annotation.

## Folders

- `scene_index/` – Individual scene metadata (POV, loot, characters, etc.)
- `raw_scene_chunks/` – Raw text of each scene (.md or .txt)
- `character_timeline/` – Character snapshots (levels, skills, titles) by day
- `timeline/` – Global event timeline by in-world time
- `aliases/` – Canonical names and aliases for characters/entities
- `metadata/` – Support files (chapters ↔ post IDs, known skills, etc.)

## Tools

Scripts will live in `scripts/` – to be added next.


### 🛠 Schema Setup

Run this to scaffold empty JSON Schema files:

```bash
./setup_schemas.sh

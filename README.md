# 🧠 Primal Hunter Metadata Index

A schema-driven, metadata system to track character progression, skills, equipment, and world state for *The Primal Hunter* series.

---

## 📘 Project Overview

This project serves as both:

* A **canonical progression tracker** for Jake and others in the *Primal Hunter* universe

It prioritizes:

* ✅ Schema-first design
* ✅ Chronological accuracy via scene- and day-level logging
* ✅ Strong tooling (validation, CLI, auto-schema setup)
* ✅ Developer learning (data modeling, CLI, Makefiles, etc.)

---

## 🧰 Directory Layout

```
primal_hunter_index/
├── canon/               # Source-of-truth data (skills, equipment, etc)
│   └── characters/      # Per-character metadata (timeline, known skills)
├── cli/                 # Interactive prompt-based data entry tools
├── tools/               # Validators, metadata consistency checks
├── schemas/             # JSON Schema definitions for all entity types
├── scene_index/         # Scene-level JSON metadata
├── chapters/            # Source markdown chapter files
├── ~notes/              # Logs, file trees, scratch space
└── Makefile             # Run everything with `make`
```

---

## ⚙️ Setup & Usage

```bash
# Clone and enter project
git clone <your-repo-url>
cd primal_hunter_index

# (Optional) Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Bootstrap missing schema stubs
make setup-schemas
```

---

## 🪄 Interactive CLI Tools

| Command              | Description                                 |
| -------------------- | ------------------------------------------- |
| `make add-skill`     | Add a skill (and optionally assign to Jake) |
| `make assign-skill`  | Add skill to character timeline             |
| `make add-equipment` | Add a new item to equipment.json            |

---

## ✅ Validators

| Command                      | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `make validate`              | Validate all `canon/` JSONs against schema   |
| `make validate-timeline`     | Validate all character `timeline.json` files |
| `make check`                 | Shortcut for `make validate`                 |
| `make validate-known-skills` | (Legacy) checks consistency of known_skills  |

---

## 📂 Visualization

| Command         | Description                                   |
| --------------- | --------------------------------------------- |
| `make filetree` | Outputs file tree (~notes/file_structure.txt) |

The tree now supports deeper nesting (`NF<=6`) to capture full character folders.

---

## 🧠 Schema Philosophy

We split metadata by purpose:

| File Type                                 | Role                                               |
| ----------------------------------------- | -------------------------------------------------- |
| `canon/skills.json`                       | Canonical list of all skills                       |
| `canon/equipment.json`                    | Canonical list of items, gear, consumables         |
| `canon/characters/jake/timeline.json`     | Time-stamped logs of Jake's growth, gear, skills   |
| `canon/characters/jake/known_skills.json` | (Deprecated) summary of known skills               |
| `schemas/*.schema.json`                   | Draft 2020-12 validation specs for every JSON type |

Each `timeline.json` entry can include:

* 🎯 Skill acquisition (`skill_log`)
* 🧠 Stat allocation & deltas
* 🧰 Equipment changes
* 🎖 Title gains
* 🧬 Resource max/current tracking
* 👹 Enemies defeated (planned)
* 🔄 Scene + day pointers for chronology

---

## 🧪 Optional: Advanced Dev Features

### Git Pre-Commit Validation

```bash
echo 'PYTHONPATH=. python tools/validate_all_metadata.py' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Future Targets

* `make test` → Run Pytest suite (schema validation, cross checks)
* `make lint` → Code quality (e.g. Ruff or Flake8)
* `make release` → Zip + archive `canon/` + schema snapshot

---

## 🧑‍💻 About

This is a **solo educational project** intended to practice:

* 🧱 Schema-first data architecture
* 🧪 Building LLM training datasets
* 🛠 Best practices in project structure and CLI design
* 📚 Systematic parsing of complex progression fantasy

LLM training accuracy improves drastically when scenes are backed by structured metadata — and that's exactly what this toolchain is for.


# --- Makefile Header ---
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
PY := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif command -v python >/dev/null 2>&1; then echo python; else command -v python3; fi)
.DEFAULT_GOAL := help

# --- Help ---
.PHONY: help
help:  ## Show available commands
	@awk 'BEGIN{FS=":.*## "; print "\nCommands:"} /^[a-zA-Z0-9_.-]+:.*## /{printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST); echo

# --- Schema Setup ---
.PHONY: setup-schemas
setup-schemas:  ## Create empty schema files for common entities (if missing)
	@mkdir -p schemas
	@for file in skills classes known_skills character_timeline titles tiers stat_scaling chapters_to_posts aliases global_event_timeline ; do \
		test -f "schemas/$$file.schema.json" || touch "schemas/$$file.schema.json"; \
		echo "✅ schemas/$$file.schema.json"; \
	done

# --- Validators ---
.PHONY: validate
validate:  ## Validate all canon/*.json against schemas
	@PYTHONPATH=. $(PY) tools/validate_all_metadata.py

.PHONY: validate-known-skills
validate-known-skills:  ## Cross-check known skills against catalog and scene IDs
	@PYTHONPATH=. $(PY) tools/validate_known_skills.py

.PHONY: validate-timeline
validate-timeline:  ## Validate character timeline files
	@PYTHONPATH=. $(PY) tools/validate_character_timeline.py

check: validate  ## Alias for validate

# --- CLI Scripts ---
.PHONY: add-skill
add-skill:  ## Launch interactive skill creation CLI
	PYTHONPATH=. $(PY) cli/add_skill.py

.PHONY: assign-skill
assign-skill:  ## Assign skill to character's timeline
	PYTHONPATH=. $(PY) cli/assign_skill_to_character_timeline.py

.PHONY: assign-skill-check
assign-skill-check:  ## Assign then validate timeline
	make assign-skill && make validate-timeline

.PHONY: add-equipment
add-equipment:  ## Launch interactive equipment CLI (if available)
	PYTHONPATH=. $(PY) cli/add_equipment.py

# --- File Tree Logging ---
.PHONY: filetree
filetree:  ## Write pruned tree to ./~notes/file_structure.txt
	@mkdir -p ./~notes
	@find . \
		\( -path './.git' -o -path './.venv' -o -path './node_modules' -o -path './__pycache__' -o -path './chapters/*' -o -path './~notes/*' \) -prune -o -print \
	| awk -F/ 'NF<=6' > ./~notes/.treelist
	@tree --fromfile ./~notes/.treelist > ./~notes/file_structure.txt
	@rm ./~notes/.treelist
	@echo "📁 Wrote ./~notes/file_structure.txt"

# --- Full Workflow ---
.PHONY: all
all: setup-schemas validate  ## Bootstrap all schemas and validate project


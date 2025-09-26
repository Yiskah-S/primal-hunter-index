# --- Makefile minimal sane header ---
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Prefer venv python, then python, then python3
PY := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif command -v python >/dev/null 2>&1; then echo python; else command -v python3; fi)

.DEFAULT_GOAL := help

.PHONY: help
help:	## show targets
	@awk 'BEGIN{FS=":.*## "; print "\nTargets:"} /^[a-zA-Z0-9_.-]+:.*## /{printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST); echo

# ----------------- targets -----------------

.PHONY: setup-schemas
setup-schemas:	## create empty schema files for common entities
	@mkdir -p schemas
	@for file in skills classes known_skills character_timeline titles tiers stat_scaling chapters_to_posts aliases global_event_timeline ; do \
		test -f "schemas/$$file.schema.json" || touch "schemas/$$file.schema.json"; \
		echo "✅ schemas/$$file.schema.json"; \
	done

.PHONY: validate
validate:	## validate all canon/*.json against schemas where available
	@$(PY) tools/validate_all_metadata.py


.PHONY: validate-known-skills
validate-known-skills:	## cross-check known skills against catalogs & scene ids
	@$(PY) tools/validate_known_skills.py


.PHONY: filetree
filetree:	## write pruned tree to ~notes/file_structure.txt
	@find . \( -path './.git' -o -path './.venv' -o -path './node_modules' -o -path './__pycache__' -o -path './chapters/*' -o -path './~notes/*' \) -prune -o -print | awk -F/ 'NF<=4' > "./~notes/.treelist"
	@tree --fromfile "./~notes/.treelist" > "./~notes/file_structure.txt"
	@rm "./~notes/.treelist"
	@echo "Wrote ./~notes/file_structure.txt"

.PHONY: all
all: setup-schemas validate	## setup schemas (if missing) and validate everything


# Run metadata validation
check:
	PYTHONPATH=. python tools/validate_all_metadata.py

# Add a new skill to canon/skills.json
add-skill:
	PYTHONPATH=. python cli/add_skill.py

# Assign a skill to a character's known_skills.json
assign-skill:
	PYTHONPATH=. python cli/assign_skill_to_character.py

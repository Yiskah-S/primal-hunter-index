
# === Primal Hunter Index Project ===
# Useful CLI commands for development, validation, and packaging

# ─── Help ─────────────────────────────────────────────────────────────────

.PHONY: help
help:  ## Show all available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'


# ─── Linting & Validation ────────────────────────────────────────────────

.PHONY: lint
lint:  ## Run Ruff linter and fix issues
	ruff check . --fix


# ─── JSON Schema Testing ─────────────────────────────────────────────────

.PHONY: test_schemas
test_schemas:  ## Run schema tests via pytest
	pytest tests/schema


# ─── Upload Bundle Creation ──────────────────────────────────────────────

.PHONY: zip_bundle
zip_bundle:  ## Create upload ZIP bundle using manifest file
	python3 tools/make_upload_bundle.py


# ─── Clean Commit (Safe Push) ────────────────────────────────────────────

.PHONY: commit_clean
commit_clean:  ## Commit known clean files with conventional message
	git add .editorconfig .gitignore Makefile README.md
	git add requirements/requirements-*.txt
	git add schemas/*.schema.json
	git commit -m "chore: clean commit of config and schemas"
	git push


# ─── File Tree Logging ───────────────────────────────────────────────────

.PHONY: filetree
filetree:  ## Write pruned file tree to /Users/jessica/Projects/z_notes
	@mkdir -p ./z_notes
	@find . \
		\( -path './.git' -o -path './.venv' -o -path './node_modules' -o -path './__pycache__' -o -path './chapters/*' -o -path './z_notes/*' \) -prune -o -print \
	| awk -F/ 'NF<=6' > ./z_notes/.treelist
	@tree --fromfile ./z_notes/.treelist > ./z_notes/file_structure.txt
	@rm ./z_notes/.treelist
	@echo "📁 Wrote ./z_notes/file_structure.txt"


# --- Makefile Header ---
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
PY := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif command -v python >/dev/null 2>&1; then echo python; else command -v python3; fi)
.DEFAULT_GOAL := help

.PHONY: validate_all
validate_all: lint test_schemas zip_bundle  ## Run linter, tests, and bundler
	@echo "✅ All validations complete."



# --- Schema Setup ---
.PHONY: setup-schemas
setup-schemas:  ## Create empty schema files for common entities (if missing)
	@mkdir -p schemas
	@for file in skills classes known_skills character_timeline titles tiers stat_scaling chapters_to_posts aliases global_event_timeline ; do \
		test -f "schemas/$$file.schema.json" || touch "schemas/$$file.schema.json"; \
		echo "✅ schemas/$$file.schema.json"; \
	done

zip:  ## Create archive of repository (excludes common noise directories)
	zip -r ../primal_hunter_index.zip . -x "*.git*" "*.venv*" "*__pycache__*" "*.DS_Store*" "*.zip"

# --- Validators ---
.PHONY: validate
validate:  ## Validate all records/*.json against schemas
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

# --- Web Helpers ---
.PHONY: json-editor
json-editor:  ## Launch records JSON editor (http://localhost:8000/tools/json_editor/)
	(sleep 1 && $(PY) -m webbrowser -t "http://localhost:8000/tools/json_editor/") &
	$(PY) -m http.server 8000

# --- Status Logs ---
.PHONY: sync_status
sync_status:  ## Copy latest z_codex_context/status_*.md into docs/logs/
	@PYTHONPATH=. $(PY) tools/sync_status.py



# --- Full Workflow ---
.PHONY: all
all: setup-schemas validate  ## Bootstrap all schemas and validate project

# --- CLI helpers ---
.PHONY: add-data
add-data:  ## Launch prompt-driven wizard to add records data
	PYTHONPATH=. $(PY) cli/add_dataset_entry.py

.PHONY: add-data-form
add-data-form:  ## Launch form-based editor for records data
	PYTHONPATH=. $(PY) cli/add_data_form.py

.PHONY: add-dataset
add-dataset:  ## Backward-compatible dataset helper (requires DATASET=...)
	@if [ -z "$(DATASET)" ]; then \
		 echo "Usage: make add-dataset DATASET=<name> [KEY=<key>] [EDIT=1] [POSITION=<n>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_dataset_entry.py $(DATASET)"; \
	 if [ -n "$(KEY)" ]; then CMD="$$CMD --key $(KEY)"; fi; \
	 if [ "$(EDIT)" = "1" ]; then CMD="$$CMD --edit"; fi; \
	 if [ -n "$(POSITION)" ]; then CMD="$$CMD --position $(POSITION)"; fi; \
	 eval "$$CMD"

.PHONY: add-scene
add-scene:  ## Create a new scene_index entry
	@if [ -z "$(SCENE_ID)" ]; then \
		 echo "Usage: make add-scene SCENE_ID=BB-CC-SS [SOURCE=<path>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_scene.py $(SCENE_ID)"; \
	 if [ -n "$(SOURCE)" ]; then CMD="$$CMD --source-file $(SOURCE)"; fi; \
	 eval "$$CMD"

.PHONY: add-timeline
add-timeline:  ## Append a timeline entry for a character
	@if [ -z "$(CHARACTER)" ]; then \
		 echo "Usage: make add-timeline CHARACTER=<name> [POSITION=<n>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_timeline_entry.py $(CHARACTER)"; \
	 if [ -n "$(POSITION)" ]; then CMD="$$CMD --position $(POSITION)"; fi; \
	 eval "$$CMD"


# ---- Search bundle wrapper for tools/search_term_mentions.py ----
# Usage:
#   make search-term SEARCH='Race: [Human'
#   make search-term SEARCH='Identify' CONTEXT=2
#   make search-term SEARCH='Identify II' REGEX=1       # treat SEARCH as regex
#
# Optional vars:
#   CHAPTERS=chapters            # where your chapter files live
#   OUT=search_results           # where bundles are written
#   CONTEXT=0                    # lines of context in manifest
#   EXT='.md,.txt'               # file extensions to scan
#   SLUG=Race_Human              # override output folder name (else auto from term)

SEARCH       ?=
REGEX        ?= 0
CHAPTERS     ?= chapters
OUT          ?= search_results
CONTEXT      ?= 0
EXT          ?= .md,.txt
SLUG         ?=

.PHONY: search-term

search-term:
	@if [ -z "$(SEARCH)" ]; then \
		echo "Error: provide SEARCH. Example:"; \
		echo "  make search-term SEARCH='Race: [Human'"; \
		exit 1; \
	fi
	@python3 tools/search_term_mentions.py \
		$(if $(filter 1,$(REGEX)),--regex,) \
		--chapters-root '$(CHAPTERS)' \
		--output-root '$(OUT)' \
		--context-lines '$(CONTEXT)' \
		--extensions '$(EXT)' \
		$(if $(SLUG),--slug '$(SLUG)',) \
		'$(SEARCH)'


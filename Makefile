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

# --- File Tree Logging ---
.PHONY: filetree
filetree:  ## Write pruned tree to ~/Projects/z_notes/file_structure.txt
	@TREE_OUT=~/Projects/z_notes/file_structure.txt ; \
	TREELIST=~/Projects/z_notes/.treelist ; \
	mkdir -p "$$(dirname $$TREE_OUT)" ; \
	find . \
		-type d \( -name '.git' -o -name '.venv' -o -name '__pycache__' -o -name 'node_modules' \) -prune -false \
		-o -type f ! -lname '*' \
		! -name '.DS_Store' \
		-print | awk -F/ 'NF<=6' > "$$TREELIST" ; \
	tree --fromfile "$$TREELIST" > "$$TREE_OUT" ; \
	rm "$$TREELIST" ; \
	echo "📁 Wrote file tree to $$TREE_OUT"



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

.PHONY: zip_bundle
zip_bundle:  ## Build uploadable zip in ./dist/
	python3 tools/make_upload_bundle.py

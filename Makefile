# -----------------------------------------------------------------------------
# Primal Hunter Index — Development Conveniences
# -----------------------------------------------------------------------------
# `make help` will list the most useful targets with a short description.
# Python tooling automatically prefers the project virtualenv when available.
# -----------------------------------------------------------------------------

SHELL       := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
PY          := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; \
	elif command -v python >/dev/null 2>&1; then echo python; \
	else command -v python3; fi)
.DEFAULT_GOAL := help

# Handy colour escapes for pretty help output.
HELP_COLOUR := \033[36m
HELP_RESET  := \033[0m

# -----------------------------------------------------------------------------
# Meta targets
# -----------------------------------------------------------------------------
.PHONY: help format lint test test-schemas validate \
	validate-known-skills validate-timeline validate-provenance validate_all \
	zip_bundle zip_bundle_dry zip_bundle_force commit_clean filetree \
	setup-schemas add-skill assign-skill assign-skill-check add-equipment \
	add-data add-data-form add-dataset add-scene add-timeline search-term \
	scrape_categories scrape_tag_pages promote-tags promote-tags-grep \
	promote-tags-all json-editor sync_status

help: ## Display available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | \
		a awk 'BEGIN {FS = ":.*## "} {printf "  $(HELP_COLOUR)%-20s$(HELP_RESET) %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Linting & tests
# -----------------------------------------------------------------------------
format: ## Auto-format Python sources with Ruff
	ruff format --config config/ruff.toml

lint: ## Run Ruff lint checks (auto-fix safe issues)
	ruff check --fix --config config/ruff.toml

test: ## Run the full pytest suite
	$(PY) -m pytest -q

test-schemas: ## Run schema-focused pytest suite
	$(PY) -m pytest tests/schema

# -----------------------------------------------------------------------------
# Validation entry points
# -----------------------------------------------------------------------------
validate: ## Validate canon JSON against schemas
	PYTHONPATH=. $(PY) tools/validate_all_metadata.py

validate-known-skills: ## Cross-check legacy known_skills catalog entries
	PYTHONPATH=. $(PY) tools/validate_known_skills.py

validate-timeline: ## Validate character timeline files
	PYTHONPATH=. $(PY) tools/validate_character_timeline.py

validate-provenance: ## Enforce provenance guardrails for canon records
	PYTHONPATH=. $(PY) tools/validate_provenance.py

validate_all: lint test-schemas validate-provenance ## One-shot: lint + schema tests + provenance
	$(PY) -m tools.validate_all_metadata

# -----------------------------------------------------------------------------
# Packaging helpers
# -----------------------------------------------------------------------------
zip_bundle: ## Build release zip without running pre-commit hooks
	$(PY) tools/make_upload_bundle.py

zip_bundle_dry: ## Show what would be included in the release zip (no pre-commit)
	$(PY) tools/make_upload_bundle.py --dry-run

zip_bundle_force: ## Force bundle creation even if checks fail
	$(PY) tools/make_upload_bundle.py --force

commit_clean: ## Example clean commit recipe for core config files
	@git add config/**/*.toml config/**/*.yaml .gitignore README.md
	@git commit -m "chore: clean commit of config updates"
	@git push

filetree: ## Emit an abbreviated project tree under ../z_notes/project_zips
	@mkdir -p ../z_notes/project_zips
	@find . \
		\( -path './.git' -o -path './.venv' -o -path './node_modules' -o -path './__pycache__' -o -path './chapters/*' -o -path './z_notes/*' \) -prune -o -print \
	| awk -F/ 'NF<=6' > ../z_notes/.treelist
	@tree --fromfile ../z_notes/.treelist > ../z_notes/project_zips/file_structure.txt
	@rm ../z_notes/.treelist
	@echo "📁 Wrote ../z_notes/project_zips/file_structure.txt"

# -----------------------------------------------------------------------------
# Bootstrap utilities
# -----------------------------------------------------------------------------
setup-schemas: ## Ensure placeholder schema files exist (legacy scaffolding)
	@mkdir -p schemas
	@for file in skills classes known_skills character_timeline titles tiers stat_scaling chapters_to_posts aliases global_event_timeline ; do \
		 test -f "schemas/$$file.schema.json" || touch "schemas/$$file.schema.json"; \
		 echo "✅ schemas/$$file.schema.json"; \
	done

# -----------------------------------------------------------------------------
# CLI helpers
# -----------------------------------------------------------------------------
add-skill: ## Launch interactive skill creation CLI
	PYTHONPATH=. $(PY) cli/add_skill.py

assign-skill: ## Assign a skill to a character timeline
	PYTHONPATH=. $(PY) cli/assign_skill_to_character_timeline.py

assign-skill-check: ## Assign skill, then validate timeline
	$(MAKE) assign-skill && $(MAKE) validate-timeline

add-equipment: ## Launch interactive equipment CLI
	PYTHONPATH=. $(PY) cli/add_equipment.py

add-data: ## Prompt-driven wizard to add records data
	PYTHONPATH=. $(PY) cli/add_dataset_entry.py

add-data-form: ## Form-based editor for records data
	PYTHONPATH=. $(PY) cli/add_data_form.py

add-dataset: ## Back-compat dataset helper (DATASET=..., optional KEY/EDIT/POSITION)
	@if [ -z "$(DATASET)" ]; then \
		 echo "Usage: make add-dataset DATASET=<name> [KEY=<key>] [EDIT=1] [POSITION=<n>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_dataset_entry.py $(DATASET)"; \
	 if [ -n "$(KEY)" ]; then CMD="$$CMD --key $(KEY)"; fi; \
	 if [ "$(EDIT)" = "1" ]; then CMD="$$CMD --edit"; fi; \
	 if [ -n "$(POSITION)" ]; then CMD="$$CMD --position $(POSITION)"; fi; \
	 eval "$$CMD"

add-scene: ## Create a new scene_index entry (SCENE_ID=BB.CC.SS)
	@if [ -z "$(SCENE_ID)" ]; then \
		 echo "Usage: make add-scene SCENE_ID=BB.CC.SS [SOURCE=<path>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_scene.py $(SCENE_ID)"; \
	 if [ -n "$(SOURCE)" ]; then CMD="$$CMD --source-file $(SOURCE)"; fi; \
	 eval "$$CMD"

add-timeline: ## Append timeline entry for a character (CHARACTER required)
	@if [ -z "$(CHARACTER)" ]; then \
		 echo "Usage: make add-timeline CHARACTER=<name> [POSITION=<n>]"; \
		 exit 1; \
	 fi; \
	 CMD="PYTHONPATH=. $(PY) cli/add_timeline_entry.py $(CHARACTER)"; \
	 if [ -n "$(POSITION)" ]; then CMD="$$CMD --position $(POSITION)"; fi; \
	 eval "$$CMD"

# -----------------------------------------------------------------------------
# Web helpers & status sync
# -----------------------------------------------------------------------------
json-editor: ## Launch local JSON editor (http://localhost:8000/tools/json_editor/)
	(sleep 1 && $(PY) -m webbrowser -t "http://localhost:8000/tools/json_editor/") &
	$(PY) -m http.server 8000

sync_status: ## Copy latest status logs into docs (automation helper)
	PYTHONPATH=. $(PY) tools/sync_status.py

# -----------------------------------------------------------------------------
# Search helpers
# -----------------------------------------------------------------------------
SEARCH ?=
REGEX  ?= 0
CHAPTERS ?= chapters
OUT ?= search_results
CONTEXT ?= 0
EXT ?= .md,.txt
SLUG ?=

search-term: ## Collect excerpts containing SEARCH term (supports REGEX=1)
	@if [ -z "$(SEARCH)" ]; then \
		echo "Error: provide SEARCH. Example:"; \
		echo "  make search-term SEARCH='Race: [Human'"; \
		exit 1; \
	fi
	@$(PY) tools/search_term_mentions.py \
		$(if $(filter 1,$(REGEX)),--regex,) \
		--chapters-root "$(CHAPTERS)" \
		--output-root "$(OUT)" \
		--context-lines "$(CONTEXT)" \
		--extensions "$(EXT)" \
		$(if $(SLUG),--slug "$(SLUG)",) \
		"$(SEARCH)"

# -----------------------------------------------------------------------------
# Tag scraping / promotion helpers
# -----------------------------------------------------------------------------
scrape_categories: ## Fetch wiki category list for tag seeds
	$(PY) tools/extract_tag_targets.py --mode categories

scrape_tag_pages: ## Fetch wiki page titles for a category
	$(PY) tools/extract_tag_targets.py --mode pages

promote-tags: ## Promote all tag candidates (dry-run by default)
	$(PY) -m tools.promote_tags --all

promote-tags-grep: ## Promote tag candidates matching REGEX (grep=<pattern>)
	$(PY) -m tools.promote_tags --grep "$(grep)"

promote-tags-all: ## Promote all tag candidates and commit
	$(PY) -m tools.promote_tags --all --commit --backup

# -----------------------------------------------------------------------------
# Provenance guardrail shortcut (keep near tagging helpers for visibility)
# -----------------------------------------------------------------------------
validate-provenance: ## One-step provenance validation (alias retained for muscle memory)
	$(PY) -m tools.validate_provenance

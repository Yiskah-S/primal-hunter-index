
# 4) New Runbooks

### 4.1 `docs/runbooks/authoring_workflow.md`

**Objective:** Generate new stories that feel canon and *cannot* smuggle fanon.

**Flow**

1. **Pitch** → short outline (beats + POV + scene targets).
2. **Preflight** → run projector at target scene(s) → produce `context_pack.json`.
3. **RAG Context Assembly** → retrieve K from each bundle; attach `context_pack`.
4. **LLM Draft** → generation with *hard constraints*:
   * Must cite `source_ref` for any mechanic claim or system rule stated.
5. **Validators** → `validate_ids`, `validate_tags`, `validate_provenance`, `check_power_scaling`.
6. **Human Review** → `.review` notes: accept, request changes, or mark as proposal.
7. **Commit** → merge draft + provenance to `drafts/` or promote to `canon/` via PR with CI gating.


- Validators: run as usual.
+ Validators:
+  - validate_tags.py --mode draft  (WARN on candidate)
+  - validate_tags.py --mode export (FAIL on non-approved)
+  - validate_ids.py, validate_provenance.py, check_power_scaling.py run in both modes

**CLI**

```
./tools/projector.py --scene 01.02.01 --out tmp/context_pack.json
./tools/export_rag_bundle.py --preset style+mech+story --out tmp/bundles/
./tools/generate.py --context tmp/context_pack.json --bundles tmp/bundles/ --draft out/draft.md
./tools/validate_all.py --path out/draft.md
```

---

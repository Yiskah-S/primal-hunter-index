(function () {
  const JSON_EDITOR_GLOBAL = window.JSONEditor;
  if (!JSON_EDITOR_GLOBAL) {
    console.error("JSONEditor script failed to load. Check network connectivity or CDN availability.");
    const container = document.getElementById("dataset-meta");
    if (container) {
      container.textContent = "⚠️ JSON Editor library failed to load";
      container.className = "form-input-hint text-error";
    }
    return;
  }

  const DATASETS = [
    {
      id: "skills",
      label: "Skills",
      schemaPath: "../../schemas/skills.schema.json",
      dataPath: "../../records/skills.json",
      metaPath: "../../records/skills.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "equipment",
      label: "Equipment",
      schemaPath: "../../schemas/equipment.schema.json",
      dataPath: "../../records/equipment.json",
      metaPath: "../../records/equipment.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "classes",
      label: "Classes",
      schemaPath: "../../schemas/classes.schema.json",
      dataPath: "../../records/classes.json",
      metaPath: "../../records/classes.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "races",
      label: "Races",
      schemaPath: "../../schemas/races.schema.json",
      dataPath: "../../records/races.json",
      metaPath: "../../records/races.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "system-glossary",
      label: "System Glossary",
      schemaPath: "../../schemas/system_glossary.schema.json",
      dataPath: "../../records/system_glossary.json",
      metaPath: "../../records/system_glossary.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "affiliations",
      label: "Affiliations",
      schemaPath: "../../schemas/affiliations.schema.json",
      dataPath: "../../records/affiliations.json",
      metaPath: "../../records/affiliations.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "creatures",
      label: "Creatures",
      schemaPath: "../../schemas/creatures.schema.json",
      dataPath: "../../records/creatures.json",
      metaPath: "../../records/creatures.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "timeline-jake",
      label: "Timeline – Jake",
      schemaPath: "../../schemas/character_timeline.schema.json",
      dataPath: "../../records/characters/jake/timeline.json",
      metaPath: "../../records/characters/jake/timeline.json.meta.json",
      entryStrategy: "array"
    },
    {
      id: "tag-registry",
      label: "Tag Registry",
      schemaPath: "../../schemas/tag_registry.schema.json",
      dataPath: "../../records/tag_registry.json",
      metaPath: "../../records/tag_registry.json.meta.json",
      entryStrategy: "object"
    },
    {
      id: "global-event-timeline",
      label: "Global Event Timeline",
      schemaPath: "../../schemas/global_event_timeline.schema.json",
      dataPath: "../../records/global_event_timeline.json",
      metaPath: "../../records/global_event_timeline.json.meta.json",
      entryStrategy: "array"
    },
    {
      id: "locations",
      label: "Locations",
      schemaPath: "../../schemas/locations.schema.json",
      dataPath: "../../records/locations.json",
      metaPath: "../../records/locations.json.meta.json",
      entryStrategy: "object"
    }
  ];

  let editor = null;
  let currentDataset = null;
  let currentSchema = null;
  let entrySchema = null;
  let currentData = null;
  let entries = [];
  let tagOptionsCache = null;

  const datasetSelect = document.getElementById("dataset-select");
  const entrySelect = document.getElementById("entry-select");
  const entryNameInput = document.getElementById("entry-name");
  const previewOutput = document.getElementById("preview-output");
  const metaSummary = document.getElementById("meta-summary");
  const datasetMeta = document.getElementById("dataset-meta");
  const toggleRaw = document.getElementById("toggle-raw");
  const provenancePreview = document.getElementById("provenance-preview");

  const sceneCache = new Map();
  let provenanceRequestToken = 0;

  function setStatus(message, isError) {
    datasetMeta.textContent = message;
    datasetMeta.className = isError ? "form-input-hint text-error" : "form-input-hint";
  }

  async function fetchJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    return response.json();
  }

  function deriveEntrySchema(schema, strategy) {
    if (strategy === "array" && schema && schema.items) {
      return schema.items;
    }
    if (schema && schema.$defs && schema.$defs.entry) {
      return schema.$defs.entry;
    }
    if (schema && schema.patternProperties) {
      const firstKey = Object.keys(schema.patternProperties)[0];
      if (firstKey) {
        return schema.patternProperties[firstKey];
      }
    }
    return schema;
  }

  function destroyEditor() {
    if (editor) {
      editor.destroy();
      editor = null;
    }
  }

  function initEditor(schema) {
    destroyEditor();
    JSON_EDITOR_GLOBAL.defaults.options.theme = "spectre";
    JSON_EDITOR_GLOBAL.defaults.options.iconlib = "spectre";
    JSON_EDITOR_GLOBAL.defaults.options.object_layout = "normal";
    JSON_EDITOR_GLOBAL.defaults.options.show_errors = "interaction";

    editor = new JSON_EDITOR_GLOBAL(document.getElementById("editor"), {
      schema,
      disable_collapse: true,
      disable_edit_json: true,
      disable_properties: false,
      show_opt_in: true
    });

    editor.on("change", updatePreview);
  }

  function populateEntrySelector(items) {
    entrySelect.innerHTML = "";
    const placeholder = document.createElement("option");
    if (!items.length) {
      placeholder.textContent = "No entries found";
      placeholder.disabled = true;
      placeholder.value = "";
      entrySelect.appendChild(placeholder);
      return;
    }
    placeholder.textContent = `Choose entry (${items.length})`;
    placeholder.value = "";
    entrySelect.appendChild(placeholder);

    items.forEach((key) => {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = key;
      entrySelect.appendChild(opt);
    });
  }

  function renderMetaSummary(meta) {
    metaSummary.innerHTML = "";
    if (!meta || typeof meta !== "object") {
      return;
    }
    const template = document.getElementById("meta-row-template");
    const addRow = (label, value) => {
      if (value === undefined || value === null || value === "") return;
      const fragment = template.content.cloneNode(true);
      fragment.querySelector("dt").textContent = label;
      fragment.querySelector("dd").textContent = value;
      metaSummary.appendChild(fragment);
    };

    addRow("records", meta.records);
    const source = meta.source || {};
    const sourceBits = [source.book, source.chapter, source.scene]
      .filter(Boolean)
      .join(" · ");
    addRow("source", sourceBits);
    addRow("scene_id", source.scene_id);
    addRow("line", source.line);
    addRow("notes", meta.notes);
    addRow("last_updated", meta.last_updated);
    addRow("entered_by", meta.entered_by);
  }

  function resetProvenancePanel() {
    if (provenancePreview) {
      provenancePreview.innerHTML = "";
    }
  }

  function normalizeSourceRefValue(sourceRef) {
    if (!sourceRef) return [];
    if (Array.isArray(sourceRef)) return sourceRef.filter((item) => item && typeof item === "object");
    if (typeof sourceRef === "object") return [sourceRef];
    return [];
  }

  function scenePathCandidates(sceneId) {
    if (typeof sceneId !== "string" || sceneId.length < 2) {
      return [];
    }
    const bookCode = sceneId.slice(0, 2);
    return [
      `../../records/scene_index/Book ${bookCode} - PH/${sceneId}.json`,
      `../../records/scene_index/${sceneId}.json`
    ];
  }

  async function fetchSceneById(sceneId) {
    if (sceneCache.has(sceneId)) {
      return sceneCache.get(sceneId);
    }
    const candidates = scenePathCandidates(sceneId);
    for (const path of candidates) {
      try {
        const scene = await fetchJson(path);
        scene.__source = path;
        sceneCache.set(sceneId, scene);
        return scene;
      } catch (error) {
        // Try the next candidate
      }
    }
    console.warn(`Scene ${sceneId} not found under known paths.`);
    sceneCache.set(sceneId, null);
    return null;
  }

  async function refreshProvenanceView(entryValue) {
    if (!provenancePreview) {
      return;
    }

    provenanceRequestToken += 1;
    const requestId = provenanceRequestToken;
    provenancePreview.innerHTML = "";

    if (!entryValue || typeof entryValue !== "object") {
      return;
    }

    const ranges = normalizeSourceRefValue(entryValue.source_ref);
    if (!ranges.length) {
      return;
    }

    const fragments = [];
    for (const range of ranges) {
      const sceneId = range.scene_id;
      const lineStart = range.line_start;
      const lineEnd = range.line_end;

      if (!sceneId) {
        fragments.push(`<li><span class="text-error">Missing scene_id on source_ref entry.</span></li>`);
        continue;
      }

      const scene = await fetchSceneById(sceneId);
      if (requestId !== provenanceRequestToken) {
        return; // stale request
      }

      if (!scene) {
        fragments.push(
          `<li><strong>${sceneId}</strong> · lines ${lineStart ?? "?"}-${lineEnd ?? "?"} · <span class="text-error">scene not found</span></li>`
        );
        continue;
      }

      const summaryBits = [scene.title, scene.summary].filter(Boolean).join(" · ");
      const lineLabel = lineStart && lineEnd ? `lines ${lineStart}-${lineEnd}` : "lines ?";
      const sourceHint = scene.__source ? ` <span class="text-gray">(${scene.__source})</span>` : "";
      const details = summaryBits ? ` · ${summaryBits}` : "";
      fragments.push(`<li><strong>${sceneId}</strong> · ${lineLabel}${details}${sourceHint}</li>`);
    }

    provenancePreview.innerHTML = fragments.join("");
  }

  function updatePreview() {
    if (!editor) {
      previewOutput.textContent = "";
      resetProvenancePanel();
      return;
    }
    try {
      const value = editor.getValue();
      const entryName = entryNameInput.value.trim();
      let payload = value;
      if (currentDataset && currentDataset.entryStrategy === "object" && entryName) {
        payload = { [entryName]: value };
      }
      const indent = toggleRaw.checked ? 0 : 2;
      previewOutput.textContent = JSON.stringify(payload, null, indent);
      refreshProvenanceView(value).catch((error) => {
        console.warn("Unable to render provenance preview:", error);
      });
    } catch (err) {
      previewOutput.textContent = `⚠️ Unable to render preview: ${err.message}`;
      resetProvenancePanel();
    }
  }

  function loadEntrySelection(key) {
    if (!editor || !currentData) return;
    if (currentDataset.entryStrategy === "array") {
      const idx = Number(key);
      if (Number.isNaN(idx) || !Array.isArray(currentData) || !currentData[idx]) {
        editor.setValue({});
        return;
      }
      editor.setValue(currentData[idx]);
      entryNameInput.value = key;
    } else {
      if (!key || !currentData[key]) {
        editor.setValue({});
        return;
      }
      editor.setValue(currentData[key]);
      entryNameInput.value = key;
    }
  }

  async function loadDataset(datasetId) {
    const dataset = DATASETS.find((item) => item.id === datasetId);
    if (!dataset) {
      setStatus("Dataset not found", true);
      return;
    }
    setStatus("Loading dataset…", false);
    try {
      const [schema, data, meta] = await Promise.all([
        fetchJson(dataset.schemaPath),
        fetchJson(dataset.dataPath),
        fetchJson(dataset.metaPath).catch(() => null)
      ]);

      currentDataset = dataset;
      currentSchema = schema;
      currentData = data;
      if (dataset.id === "tag-registry") {
        tagOptionsCache = buildTagOptions(data);
      }

      entrySchema = deriveEntrySchema(schema, dataset.entryStrategy);

      if (dataset.id !== "tag-registry") {
        const tagOptions = await ensureTagOptions();
        entrySchema = decorateSchemaWithTags(entrySchema, tagOptions);
      }

      initEditor(entrySchema);

      if (Array.isArray(data)) {
        entries = data.map((_, idx) => idx.toString());
      } else if (data && typeof data === "object") {
        entries = Object.keys(data).sort((a, b) => a.localeCompare(b));
      } else {
        entries = [];
      }
      populateEntrySelector(entries);
      renderMetaSummary(meta);
      entryNameInput.value = "";
      previewOutput.textContent = "";
      resetProvenancePanel();
      setStatus(`Loaded schema and ${entries.length} entries`, false);
    } catch (err) {
      console.error(err);
      destroyEditor();
      currentDataset = null;
      setStatus(err.message, true);
    }
  }

  function handleDownload() {
    if (!editor) return;
    const value = editor.getValue();
    const entryName = entryNameInput.value.trim();

    let filename = `${currentDataset ? currentDataset.id : "entry"}.json`;
    let payload = value;

    if (currentDataset && currentDataset.entryStrategy === "object") {
      if (!entryName) {
        alert("Please provide an entry key before downloading.");
        return;
      }
      payload = { [entryName]: value };
      filename = `${entryName.replace(/\s+/g, "_") || "entry"}.json`;
    } else if (currentDataset && currentDataset.entryStrategy === "array") {
      filename = `${currentDataset.id}-entry.json`;
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  }

  function clearEditor() {
    if (!editor) return;
    editor.setValue({});
    entrySelect.value = "";
    previewOutput.textContent = "";
    resetProvenancePanel();
  }

  function populateDatasets() {
    DATASETS.forEach((dataset) => {
      const opt = document.createElement("option");
      opt.value = dataset.id;
      opt.textContent = dataset.label;
      datasetSelect.appendChild(opt);
    });
  }

  // Event bindings
  datasetSelect.addEventListener("change", (event) => {
    const datasetId = event.target.value;
    if (datasetId) {
      loadDataset(datasetId);
    }
  });

  entrySelect.addEventListener("change", (event) => {
    const key = event.target.value;
    loadEntrySelection(key);
  });

  document.getElementById("download-entry").addEventListener("click", handleDownload);
  document.getElementById("clear-editor").addEventListener("click", clearEditor);
  document.getElementById("refresh-dataset").addEventListener("click", () => {
    if (currentDataset) {
      loadDataset(currentDataset.id);
    }
  });

  toggleRaw.addEventListener("change", updatePreview);
  entryNameInput.addEventListener("input", updatePreview);

  // Initialize
  populateDatasets();
  if (DATASETS.length) {
    datasetSelect.value = DATASETS[0].id;
    loadDataset(DATASETS[0].id);
  }
})();
  function buildTagOptions(registry) {
    if (!registry || typeof registry !== "object") {
      return null;
    }
    const classes = registry.tag_classes || {};
    const tags = registry.tags || {};
    const values = [];
    const titles = [];
    const groups = [];

    const classOrder = Object.keys(classes).sort((a, b) =>
      (classes[a]?.label || a).localeCompare(classes[b]?.label || b)
    );
    const buckets = new Map();
    for (const classId of classOrder) {
      buckets.set(classId, []);
    }
    for (const [tagId, meta] of Object.entries(tags)) {
      const classId = typeof meta?.class === "string" ? meta.class : "other";
      if (!buckets.has(classId)) {
        buckets.set(classId, []);
      }
      buckets.get(classId).push({
        id: tagId,
        allowInferred: Boolean(meta?.allow_inferred)
      });
    }

    const sortedBuckets = Array.from(buckets.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    for (const [classId, tagList] of sortedBuckets) {
      if (!tagList.length) continue;
      const classLabel = (classes[classId]?.description ? classes[classId].description : "").trim();
      const friendlyClassName = classId.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      tagList.sort((a, b) => a.id.localeCompare(b.id));
      for (const tag of tagList) {
        values.push(tag.id);
        const humanName = tag.id.replace(/_/g, " ");
        const titleParts = [friendlyClassName, "›", humanName];
        if (tag.allowInferred) {
          titleParts.push("(inferred ok)");
        }
        titles.push(titleParts.join(" "));
        groups.push(friendlyClassName);
      }
    }

    return { values, titles, groups };
  }

  async function ensureTagOptions() {
    if (tagOptionsCache) {
      return tagOptionsCache;
    }
    try {
      const registry = await fetchJson("../../records/tag_registry.json");
      tagOptionsCache = buildTagOptions(registry);
    } catch (error) {
      console.warn("Failed to load tag registry:", error);
      tagOptionsCache = null;
    }
    return tagOptionsCache;
  }

  function cloneSchema(node) {
    return node ? JSON.parse(JSON.stringify(node)) : node;
  }

  function decorateSchemaWithTags(schema, tagOptions) {
    if (!schema || !tagOptions || !tagOptions.values?.length) {
      return schema;
    }

    const decorated = cloneSchema(schema);

    function walk(node, pointerSegment) {
      if (!node || typeof node !== "object") {
        return;
      }

      if (
        node.type === "array" &&
        pointerSegment === "tags" &&
        (!node.items || typeof node.items === "object")
      ) {
        node.items = node.items && typeof node.items === "object" ? node.items : {};
        node.items.type = node.items.type || "string";
        node.items.enum = tagOptions.values;
        node.items.options = node.items.options || {};
        node.items.options.enum_titles = tagOptions.titles;
        node.items.options.enum_groups = tagOptions.groups;
        node.uniqueItems = node.uniqueItems !== undefined ? node.uniqueItems : true;
        node.format = node.format || "select";
      }

      if (node.properties && typeof node.properties === "object") {
        for (const [childKey, childNode] of Object.entries(node.properties)) {
          walk(childNode, childKey);
        }
      }

      if (node.patternProperties && typeof node.patternProperties === "object") {
        for (const childNode of Object.values(node.patternProperties)) {
          walk(childNode, pointerSegment);
        }
      }

      if (node.items) {
        if (Array.isArray(node.items)) {
          node.items.forEach((child) => walk(child, pointerSegment));
        } else {
          walk(node.items, pointerSegment);
        }
      }

      if (node.anyOf) {
        node.anyOf.forEach((child) => walk(child, pointerSegment));
      }
      if (node.oneOf) {
        node.oneOf.forEach((child) => walk(child, pointerSegment));
      }
      if (node.allOf) {
        node.allOf.forEach((child) => walk(child, pointerSegment));
      }
      if (node.$defs) {
        Object.values(node.$defs).forEach((child) => walk(child, pointerSegment));
      }
      if (node.definitions) {
        Object.values(node.definitions).forEach((child) => walk(child, pointerSegment));
      }
    }

    walk(decorated, "");
    return decorated;
  }

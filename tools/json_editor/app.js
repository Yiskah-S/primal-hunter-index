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
      id: "timeline-jake",
      label: "Timeline – Jake",
      schemaPath: "../../schemas/character_timeline.schema.json",
      dataPath: "../../records/characters/jake/timeline.json",
      metaPath: "../../records/characters/jake/timeline.json.meta.json",
      entryStrategy: "array"
    }
  ];

  let editor = null;
  let currentDataset = null;
  let currentSchema = null;
  let entrySchema = null;
  let currentData = null;
  let entries = [];

  const datasetSelect = document.getElementById("dataset-select");
  const entrySelect = document.getElementById("entry-select");
  const entryNameInput = document.getElementById("entry-name");
  const previewOutput = document.getElementById("preview-output");
  const metaSummary = document.getElementById("meta-summary");
  const datasetMeta = document.getElementById("dataset-meta");
  const toggleRaw = document.getElementById("toggle-raw");

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

  function updatePreview() {
    if (!editor) {
      previewOutput.textContent = "";
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
    } catch (err) {
      previewOutput.textContent = `⚠️ Unable to render preview: ${err.message}`;
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
      entrySchema = deriveEntrySchema(schema, dataset.entryStrategy);
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

const form = document.getElementById("contribute-form");
const list = document.getElementById("node-list");
const preview = document.getElementById("address-preview");
const statusEl = document.getElementById("form-status");
const robustnessLens = document.getElementById("robustness-lens");

function addressFromForm(data) {
  return `UPI<${data.get("domain")},${data.get("generation")},${data.get("torus")},${data.get("node")}>`;
}

function refreshPreview() {
  const data = new FormData(form);
  preview.textContent = addressFromForm(data);
}

["domain", "generation", "torus", "node"].forEach((name) => {
  form.elements[name].addEventListener("input", refreshPreview);
});
refreshPreview();

function renderNode(node, prepend = false) {
  const item = document.createElement("li");
  const payload = node.payload || {};
  const view = node.status_view || { display_status: node.status };
  const statusLabel = view.promoted
    ? `${view.display_status} (${view.scope}) · canonical ${view.canonical_status}`
    : view.display_status;
  const title = document.createElement("strong");
  title.textContent = payload.title || node.title;
  const status = document.createElement("div");
  status.className = "status";
  status.textContent = `${statusLabel} · ${node.address}`;
  const description = document.createElement("p");
  description.textContent = payload.description || "";
  item.append(title, status, description);
  if (prepend) list.prepend(item);
  else list.append(item);
}

async function loadNodes() {
  const box = document.getElementById("search-box");
  const params = new URLSearchParams();
  if (box && box.value) params.set("q", box.value);
  if (robustnessLens && robustnessLens.checked) {
    params.set("evidence_lens", "linked-robustness");
  }
  const query = params.toString();
  const response = await fetch(`/api/nodes${query ? `?${query}` : ""}`);
  const body = await response.json();
  list.replaceChildren();
  (body.nodes || []).forEach((node) => renderNode(node));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "Validating…";
  statusEl.className = "";
  const data = new FormData(form);
  const payload = {
    address: addressFromForm(data),
    title: data.get("title"),
    description: data.get("description"),
    status: data.get("status"),
    information_layer: "PUBLIC",
    verification_type: "software_test",
    claims_experimental_verification: false,
    confusion_guard: data.get("confusion_guard") || undefined,
  };
  if (data.get("equation")) payload.equations = [data.get("equation")];
  if (data.get("evidence_source")) {
    payload.evidence = [{ type: "other", source: data.get("evidence_source") }];
    payload.primary_sources = [data.get("evidence_source")];
  }
  if (data.get("falsification")) payload.falsification_conditions = [data.get("falsification")];
  if (data.get("stop_reason")) payload.stop_reason = data.get("stop_reason");

  const response = await fetch("/api/nodes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  if (!response.ok) {
    statusEl.textContent = (body.errors || ["rejected"]).join(" · ");
    statusEl.className = "bad";
    return;
  }
  statusEl.textContent = `Added ${body.address}`;
  statusEl.className = "ok";
  form.reset();
  form.elements.status.value = "SYM";
  refreshPreview();
});

function listen() {
  const stream = new EventSource("/api/events");
  stream.onmessage = (message) => {
    const event = JSON.parse(message.data);
    if (event.kind === "contribution") loadNodes();
  };
}

loadNodes().catch(() => {
  statusEl.textContent = "Could not load the live index.";
  statusEl.className = "bad";
});
listen();
const searchBox = document.getElementById("search-box");
if (searchBox) searchBox.addEventListener("input", () => loadNodes());
if (robustnessLens) robustnessLens.addEventListener("change", () => loadNodes());

const ingestStatus = document.getElementById("ingest-status");
const batchFile = document.getElementById("batch-file");

async function ingest(mode) {
  if (!batchFile.files.length) {
    ingestStatus.textContent = "Choose a JSON batch file first.";
    ingestStatus.className = "bad";
    return;
  }
  ingestStatus.textContent = mode === "check" ? "Checking…" : "Inserting…";
  ingestStatus.className = "";
  const text = await batchFile.files[0].text();
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    ingestStatus.textContent = "File is not valid JSON.";
    ingestStatus.className = "bad";
    return;
  }
  const response = await fetch(`/api/ingest?mode=${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  ingestStatus.textContent = JSON.stringify(body, null, 2);
  ingestStatus.className = body.ok ? "ok" : "bad";
  if (mode === "insert") loadNodes();
}

document.getElementById("check-batch").addEventListener("click", () => ingest("check"));
document.getElementById("insert-batch").addEventListener("click", () => ingest("insert"));

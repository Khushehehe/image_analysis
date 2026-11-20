const input = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const previewWrap = document.getElementById("previewWrap");
const preview = document.getElementById("preview");
const fileName = document.getElementById("fileName");
const analyzeBtn = document.getElementById("analyzeBtn");
const removeBtn = document.getElementById("removeBtn");
let selectedFile = null;

function setFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) { alert("Please select an image file."); return; }
  if (file.size > 8 * 1024 * 1024) { alert("Image must be smaller than 8 MB."); return; }
  selectedFile = file;
  preview.src = URL.createObjectURL(file);
  fileName.textContent = file.name;
  previewWrap.hidden = false;
  analyzeBtn.disabled = false;
}
input.addEventListener("change", e => setFile(e.target.files[0]));
removeBtn.addEventListener("click", () => {
  selectedFile = null; input.value = ""; preview.src = "";
  previewWrap.hidden = true; fileName.textContent = "Choose an image to begin";
  analyzeBtn.disabled = true;
});
["dragenter","dragover"].forEach(ev => dropzone.addEventListener(ev, e => {e.preventDefault();dropzone.classList.add("drag");}));
["dragleave","drop"].forEach(ev => dropzone.addEventListener(ev, e => {e.preventDefault();dropzone.classList.remove("drag");}));
dropzone.addEventListener("drop", e => setFile(e.dataTransfer.files[0]));

function renderResults(data) {
  document.getElementById("emptyState").hidden = true;
  document.getElementById("results").hidden = false;
  document.getElementById("modeNote").textContent = data._mode || "";
  document.getElementById("caption").textContent =
    data.captionResult?.text || data.captionResult?.values?.[0]?.text || "No caption returned.";
  const tags = data.tagsResult?.values || [];
  document.getElementById("tags").innerHTML = tags.length
    ? tags.map(t => `<span class="chip">${escapeHtml(t.name)} · ${Math.round((t.confidence || 0)*100)}%</span>`).join("")
    : '<span class="object-list">No tags returned.</span>';
  const objects = data.objectsResult?.values || [];
  document.getElementById("objects").textContent = objects.length
    ? objects.map(o => `${o.tags?.[0]?.name || "Object"} (${Math.round((o.tags?.[0]?.confidence || 0)*100)}%)`).join(" · ")
    : "No objects returned.";
  const blocks = data.readResult?.blocks || [];
  const lines = blocks.flatMap(b => (b.lines || []).map(line => line.text));
  document.getElementById("ocr").textContent = lines.length ? lines.join("\n") : "No readable text detected.";
}
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  analyzeBtn.disabled = true; analyzeBtn.textContent = "Analyzing image…";
  document.getElementById("status").textContent = "PROCESSING";
  const form = new FormData(); form.append("image", selectedFile);
  try {
    const response = await fetch("/analyze", {method:"POST", body:form});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed.");
    renderResults(data);
    document.getElementById("status").textContent = "ANALYSIS COMPLETE";
  } catch (err) {
    alert(err.message);
    document.getElementById("status").textContent = "ANALYSIS FAILED";
  } finally {
    analyzeBtn.disabled = false; analyzeBtn.textContent = "✦ Analyze image";
  }
});

// Page logic. Everything except the language choice lives only in memory.
const $ = (id) => document.getElementById(id);
const views = ["language-view", "upload-view", "processing-view", "message-view", "results-view"];
let currentView = "upload-view";

const ICONS = {
  deadline: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3.5 10h17M8 3v4M16 3v4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  action: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M7.5 12.5l3 3 6-6.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  docs: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h8l4 4v14H6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 12h6M9 16h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  contact: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3.5l3 .8 1 4-2 1.5a12 12 0 005.7 5.7l1.5-2 4 1 .8 3a2 2 0 01-2 2.4A15.5 15.5 0 013.5 5.5a2 2 0 012.400-2z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
  flag: '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.500l9.500 17h-19z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 10v5M12 17.800v.2" fill="none" stroke="currentColor" stroke-width="2.200" stroke-linecap="round"/></svg>',
};
ICONS.what = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 11v6M12 7.5v.1" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
const KIND_LABEL = { deadline: "kindDeadline", action: "kindAction", docs: "kindDocs", contact: "kindContact", flag: "kindFlag" };

let result = null; // the current LetterResult (memory only)
let lastError = null;

function show(viewId, { intro = false } = {}) {
  currentView = viewId;
  for (const v of views) $(v).hidden = v !== viewId;
  $("intro").hidden = !intro;
}

function renderToggle() {
  const wrap = $("topbar-right");
  wrap.innerHTML = "";
  if (!currentLangChosen) return;
  const group = document.createElement("div");
  group.className = "lang-toggle";
  group.setAttribute("role", "group");
  group.setAttribute("aria-label", t("langLabel"));
  for (const [code, label] of [["es", "Español"], ["en", "English"]]) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.lang = code;
    b.setAttribute("aria-pressed", String(currentLang === code));
    b.addEventListener("click", () => setLang(code));
    group.appendChild(b);
  }
  wrap.appendChild(group);
}

let currentLangChosen = false;
function setLang(code) {
  currentLang = code;
  currentLangChosen = true;
  try { localStorage.setItem(LANG_KEY, code); } catch (e) { /* private mode: fine */ }
  const wasPicker = currentView === "language-view";
  applyStaticText();
  renderToggle();
  renderFooter();
  if (wasPicker) return show("upload-view", { intro: true });
  // Re-draw whatever is on screen in the new language, keeping the results in memory.
  if (currentView === "results-view" && result) renderResults();
  else if (currentView === "message-view") renderMessage(lastError);
  else if (currentView === "processing-view") renderProcessing();
}

let disclosuresOpen = false;
function renderFooter() {
  const f = $("footer");
  f.innerHTML = "";
  const note = document.createElement("p");
  note.className = "notice";
  note.textContent = t("notLegal");
  const link = document.createElement("button");
  link.className = "link";
  link.type = "button";
  link.textContent = t("disclosuresLink");
  link.setAttribute("aria-expanded", String(disclosuresOpen));
  link.addEventListener("click", () => { disclosuresOpen = !disclosuresOpen; renderFooter(); });
  f.append(note, link);
  if (disclosuresOpen) {
    const panel = document.createElement("div");
    panel.className = "disclosures";
    const h = document.createElement("h2");
    h.textContent = t("disclosuresTitle");
    h.style.fontSize = "1.1rem";
    panel.appendChild(h);
    for (const k of ["disclosures1", "disclosures2", "disclosures3", "disclosures4", "disclosures5"]) {
      const p = document.createElement("p");
      p.textContent = t(k);
      panel.appendChild(p);
    }
    f.appendChild(panel);
  }
}

function applyStaticText() {
  document.documentElement.lang = currentLang;
  $("app-name").textContent = t("appName");
  $("greeting").textContent = t("greeting");
  $("explain").textContent = t("explain");
  $("dz-main").textContent = t("dzMain");
  $("dz-sub").textContent = t("dzSub");
}

function renderProcessing() {
  const el = $("processing-view");
  el.innerHTML = "";
  const box = document.createElement("div");
  box.className = "processing";
  box.setAttribute("role", "status");
  box.innerHTML = `<div class="paper-anim"><span></span><span></span><span></span><span></span></div>
    <h2></h2><p></p>`;
  box.querySelector("h2").textContent = t("processingTitle");
  box.querySelector("p").textContent = t("processingText");
  el.appendChild(box);
}

function renderMessage(code) {
  lastError = code;
  const map = { cannot_read: "errCannotRead", unsupported_in_mode: "errUnsupported", provider_error: "errProvider", network: "errNetwork" };
  const el = $("message-view");
  el.innerHTML = "";
  const box = document.createElement("div");
  box.className = "box message";
  box.setAttribute("role", "alert");
  const p = document.createElement("p");
  p.textContent = t(map[code] || "errProvider");
  const btn = document.createElement("button");
  btn.textContent = t("tryAgain");
  btn.addEventListener("click", startOver);
  box.append(p, btn);
  el.appendChild(box);
  show("message-view");
}

function sentenceEl(s, kind, unverifiedIds) {
  const el = document.createElement("span");
  el.className = "sentence";
  el.dataset.id = s.id;
  if (kind) {
    el.classList.add("hl");
    el.dataset.kind = kind;
    el.tabIndex = 0;
    el.setAttribute("role", "button");
    el.insertAdjacentHTML("beforeend", ICONS[kind]);
  }
  const num = document.createElement("span");
  num.className = "sentence-id";
  num.textContent = s.id;
  el.append(num, document.createTextNode(s.text));
  if (unverifiedIds && unverifiedIds.has(s.id)) {
    const u = document.createElement("span");
    u.className = "unverified";
    u.textContent = t("translationCheck");
    el.append(" ", u);
  }
  return el;
}

function letterColumn(id, headingKey, sentences, kinds, lang, unverifiedIds) {
  const col = document.createElement("section");
  col.className = "letter";
  col.id = id;
  if (lang) col.lang = lang;
  const h = document.createElement("h2");
  h.textContent = t(headingKey);
  col.appendChild(h);
  for (const s of sentences) col.appendChild(sentenceEl(s, kinds.get(s.id), unverifiedIds));
  return col;
}

function cautionBox(title, text) {
  const box = document.createElement("div");
  box.className = "box caution";
  box.setAttribute("role", "note");
  const h = document.createElement("h2");
  h.textContent = title;
  const p = document.createElement("p");
  p.textContent = text;
  box.append(h, p);
  return box;
}

function incompleteText() {
  const reason = currentLang === "es" ? result.incomplete_reason_es : result.incomplete_reason_en;
  return [reason, t("cautionIncompleteText")].filter(Boolean).join(" ");
}

function renderCautions(parent) {
  const w = result.warnings;
  if (w.includes("past_deadline")) parent.appendChild(cautionBox(t("cautionPastTitle"), t("cautionPastText")));
  if (w.includes("incomplete")) parent.appendChild(cautionBox(t("cautionIncompleteTitle"), incompleteText()));
  if (w.includes("image_source")) parent.appendChild(cautionBox(t("cautionImageTitle"), t("cautionImageText")));
}

function summaryItemEl(item, index) {
  const row = document.createElement("div");
  row.className = "summary-item";
  row.dataset.index = index;
  const badge = document.createElement("span");
  badge.className = "badge";
  badge.dataset.kind = item.kind;
  badge.innerHTML = ICONS[item.kind] || "";
  const body = document.createElement("div");
  const label = document.createElement("span");
  label.className = "label";
  label.textContent = t(item.kind === "what" ? "kindWhat" : KIND_LABEL[item.kind]);
  const text = document.createElement("span");
  text.className = "text";
  text.textContent = currentLang === "es" ? item.text_es : item.text_en;
  body.append(label, text);
  if (!item.verified) {
    const u = document.createElement("span");
    u.className = "unverified";
    u.textContent = t("unverified");
    body.append(document.createElement("br"), u);
  }
  if (item.kind !== "what" && item.sentence_ids.length) {
    const btn = document.createElement("button");
    btn.className = "link";
    btn.textContent = t("showInLetter");
    btn.addEventListener("click", () => showInLetter(item.sentence_ids));
    body.append(document.createElement("br"), btn);
  }
  row.append(badge, body);
  return row;
}

function renderSummary(parent) {
  const box = document.createElement("section");
  box.className = "summary";
  const h = document.createElement("h2");
  h.textContent = t("summaryHeading");
  box.appendChild(h);
  result.summary.forEach((item, i) => box.appendChild(summaryItemEl(item, i)));
  parent.appendChild(box);
}

function flash(el) {
  el.classList.remove("flash");
  void el.offsetWidth; // restart the animation
  el.classList.add("flash");
}

function showInLetter(ids) {
  let first = true;
  for (const id of ids) {
    for (const col of ["letter-original", "letter-translation"]) {
      const el = document.querySelector(`#${col} .sentence[data-id="${id}"]`);
      if (!el) continue;
      if (first && col === "letter-original") { el.scrollIntoView({ behavior: "smooth", block: "center" }); first = false; }
      flash(el);
    }
  }
}

let tipTimer = null;
function showTooltip(el, kind) {
  hideTooltip();
  const tip = document.createElement("div");
  tip.className = "tooltip";
  tip.id = "tooltip";
  tip.setAttribute("role", "status");
  tip.textContent = t("tip" + kind[0].toUpperCase() + kind.slice(1));
  document.body.appendChild(tip);
  const r = el.getBoundingClientRect();
  tip.style.left = Math.max(8, Math.min(window.scrollX + r.left, window.scrollX + window.innerWidth - tip.offsetWidth - 8)) + "px";
  tip.style.top = window.scrollY + r.bottom + 6 + "px";
  tipTimer = setTimeout(hideTooltip, 3500);
}
function hideTooltip() {
  clearTimeout(tipTimer);
  const old = $("tooltip");
  if (old) old.remove();
}

function onHighlightActivate(el) {
  const twinCol = el.closest("#letter-original") ? "letter-translation" : "letter-original";
  const twin = document.querySelector(`#${twinCol} .sentence[data-id="${el.dataset.id}"]`);
  if (twin) {
    flash(twin);
    const r = twin.getBoundingClientRect();
    if (r.top < 70 || r.bottom > window.innerHeight) twin.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  showTooltip(el, el.dataset.kind);
}

let scamAcknowledged = false;

function renderScamWarning() {
  const box = document.createElement("section");
  box.className = "box scam";
  box.setAttribute("role", "alert");
  const h = document.createElement("h2");
  h.textContent = t("scamTitle");
  const intro = document.createElement("p");
  intro.textContent = t("scamIntro");
  const ul = document.createElement("ul");
  for (const r of currentLang === "es" ? result.scam.reasons_es : result.scam.reasons_en) {
    const li = document.createElement("li");
    li.textContent = r;
    ul.appendChild(li);
  }
  const advice = document.createElement("p");
  advice.innerHTML = "<strong></strong>";
  advice.firstChild.textContent = t("scamAdvice");
  const label = document.createElement("label");
  label.className = "ack";
  const cb = document.createElement("input");
  cb.type = "checkbox";
  cb.checked = scamAcknowledged;
  cb.addEventListener("change", () => {
    scamAcknowledged = cb.checked;
    $("results-content").hidden = !cb.checked;
  });
  label.append(cb, document.createTextNode(t("scamAck")));
  box.append(h, intro, ul, advice, label);
  return box;
}

function renderResults() {
  const el = $("results-view");
  el.innerHTML = "";
  const scamBox = result.scam.flagged ? renderScamWarning() : null;
  if (scamBox) el.appendChild(scamBox);
  const content = document.createElement("div");
  content.id = "results-content";
  content.hidden = Boolean(scamBox) && !scamAcknowledged;
  el.appendChild(content);
  renderCautions(content);
  const kinds = new Map(result.highlights.map((h) => [h.sentence_id, h.kind]));
  const letters = document.createElement("div");
  letters.className = "letters";
  letters.append(
    letterColumn("letter-original", "originalHeading", result.original, kinds, "en"),
    letterColumn("letter-translation", "translationHeading", result.translation, kinds, "es", new Set(result.unverified_translation_ids)),
  );
  letters.addEventListener("click", (e) => {
    const hl = e.target.closest(".sentence.hl");
    if (hl) onHighlightActivate(hl);
  });
  letters.addEventListener("keydown", (e) => {
    const hl = e.target.closest(".sentence.hl");
    if (hl && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); onHighlightActivate(hl); }
  });
  content.appendChild(letters);
  renderSummary(content);

  const row = document.createElement("div");
  row.className = "actions-row";
  const again = document.createElement("button");
  again.textContent = t("startOver");
  again.addEventListener("click", startOver);
  row.append(again);
  content.appendChild(row);
  show("results-view");
}

async function upload(file) {
  show("processing-view");
  renderProcessing();
  try {
    const res = await fetch("/api/explain", { method: "POST", body: formData(file) });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) return renderMessage(body.code || "provider_error");
    result = body;
    scamAcknowledged = false;
    renderResults();
  } catch (e) {
    renderMessage("network");
  }
}

function formData(file) {
  const fd = new FormData();
  fd.append("file", file);
  return fd;
}

function startOver() {
  hideTooltip();
  scamAcknowledged = false;
  result = null;
  lastError = null;
  $("file-input").value = "";
  $("results-view").innerHTML = "";
  $("message-view").innerHTML = "";
  show("upload-view", { intro: true });
}

function setupUpload() {
  const dz = $("dropzone");
  const input = $("file-input");
  input.addEventListener("change", () => input.files[0] && upload(input.files[0]));
  dz.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
  });
  ["dragenter", "dragover"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("drag"); }));
  ["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("drag"); }));
  dz.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (f) upload(f); });
}

function init() {
  let stored = null;
  try { stored = localStorage.getItem(LANG_KEY); } catch (e) { /* ignore */ }
  setupUpload();
  document.querySelectorAll("#language-view [data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
  if (stored === "es" || stored === "en") {
    currentLang = stored;
    currentLangChosen = true;
    applyStaticText();
    renderToggle();
    renderFooter();
    show("upload-view", { intro: true });
  } else {
    currentLang = "es";
    applyStaticText();
    renderFooter();
    show("language-view");
  }
}
init();

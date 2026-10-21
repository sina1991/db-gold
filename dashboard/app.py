from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .modules.registry import list_modules

BASE_DIR = Path(__file__).resolve().parent
THEMES_DIR = BASE_DIR / "themes"
THEME_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")

app = FastAPI(
    title="XAUUSD Dashboard",
    description="Independent theme-based dashboard shell.",
    version="0.2.0",
)


def load_themes() -> list[dict]:
    themes = []
    for path in sorted(THEMES_DIR.glob("*.json")):
        try:
            theme = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid theme file: {path.name}",
            ) from exc

        if not isinstance(theme, dict) or not isinstance(theme.get("id"), str):
            raise HTTPException(
                status_code=500,
                detail=f"Theme metadata is invalid: {path.name}",
            )

        if theme["id"] != path.stem:
            raise HTTPException(
                status_code=500,
                detail=f"Theme id must match filename: {path.name}",
            )

        if not isinstance(theme.get("slots"), list):
            raise HTTPException(
                status_code=500,
                detail=f"Theme slots are invalid: {path.name}",
            )

        themes.append(theme)

    return themes


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "xauusd-dashboard"}


@app.get("/api/themes")
def list_themes() -> dict:
    themes = load_themes()
    return {
        "count": len(themes),
        "themes": [
            {
                "id": theme["id"],
                "name": theme["name"],
                "version": theme["version"],
                "slot_count": len(theme["slots"]),
            }
            for theme in themes
        ],
    }


@app.get("/api/themes/{theme_id}")
def get_theme(theme_id: str) -> dict:
    if not THEME_ID_PATTERN.fullmatch(theme_id):
        raise HTTPException(status_code=404, detail="Theme not found")

    for theme in load_themes():
        if theme["id"] == theme_id:
            return theme

    raise HTTPException(status_code=404, detail="Theme not found")


@app.get("/api/modules")
def api_modules() -> dict:
    modules = list_modules()
    return {"count": len(modules), "modules": modules}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return PAGE


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>XAUUSD Dashboard</title>
<style>
:root {
  color-scheme: dark;
  --bg: #0b1120;
  --panel: #121c2e;
  --border: #29374c;
  --muted: #91a2bb;
  --text: #e7edf7;
  --accent: #60a5fa;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 14px/1.5 system-ui, sans-serif;
}
header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 20px 24px; border-bottom: 1px solid var(--border);
  background: #0f1728; flex-wrap: wrap;
}
h1 { margin: 0; font-size: 21px; }
.subtitle { color: var(--muted); margin-top: 3px; }
.controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
label { color: var(--muted); }
select {
  background: var(--panel); color: var(--text); border: 1px solid var(--border);
  padding: 9px 10px; border-radius: 8px; min-width: 0; max-width: 100%;
}
#theme { min-width: 180px; }
main { padding: 22px 24px; max-width: 1800px; margin: auto; }
.toolbar {
  display: flex; justify-content: space-between; gap: 12px;
  align-items: center; margin-bottom: 16px; flex-wrap: wrap;
}
#theme-info, #status { color: var(--muted); }
#grid {
  display: grid;
  grid-template-columns: repeat(var(--theme-columns, 12), minmax(0, 1fr));
  gap: 12px; align-items: stretch;
}
.slot {
  min-width: 0; min-height: 190px; background: var(--panel);
  border: 1px solid var(--border); border-radius: 12px;
  padding: 14px; display: flex; flex-direction: column; gap: 12px;
}
.slot-head {
  display: flex; justify-content: space-between; align-items: center; gap: 8px;
}
.slot-name { font-weight: 650; overflow-wrap: anywhere; }
.slot-index { color: var(--muted); font-size: 12px; flex-shrink: 0; }
.slot-controls { display: grid; gap: 5px; }
.slot-controls label { font-size: 12px; }
.module-select { width: 100%; }
.module-body {
  flex: 1; min-width: 0; display: flex; flex-direction: column;
  gap: 8px; color: var(--muted);
}
.module-title { color: var(--text); font-weight: 600; }
.module-detail { overflow-wrap: anywhere; }
.module-status {
  display: inline-flex; align-self: flex-start; border: 1px solid var(--border);
  border-radius: 7px; padding: 3px 8px; font-size: 12px;
}
.module-note-input {
  width: 100%; min-height: 70px; resize: vertical; padding: 9px;
  color: var(--text); background: #0b1120; border: 1px solid var(--border);
  border-radius: 8px; font: inherit;
}
.empty { color: var(--muted); }
footer { color: var(--muted); padding: 22px 24px; border-top: 1px solid var(--border); }
@media (max-width: 900px) {
  #grid { grid-template-columns: repeat(6, minmax(0, 1fr)); }
  .slot { grid-column: span 3 !important; grid-row: auto !important; }
}
@media (max-width: 560px) {
  header, main { padding: 16px; }
  #grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .slot { grid-column: span 2 !important; }
  #theme { min-width: 0; width: 100%; }
}
</style>
</head>
<body>
<header>
  <div>
    <h1>XAUUSD Dashboard</h1>
    <div class="subtitle">Independent, theme-based workspace</div>
  </div>
  <div class="controls">
    <label for="theme">Theme</label>
    <select id="theme" aria-label="Select dashboard theme"></select>
  </div>
</header>
<main>
  <div class="toolbar">
    <div id="theme-info">Loading themes…</div>
    <div id="status" role="status">Starting</div>
  </div>
  <section id="grid" aria-label="Dashboard slots"></section>
</main>
<footer>Dashboard shell · Slot module selection is stored in this browser.</footer>

<script>
"use strict";

const themeSelect = document.getElementById("theme");
const grid = document.getElementById("grid");
const themeInfo = document.getElementById("theme-info");
const statusText = document.getElementById("status");

const STORAGE_KEY = "xauusd-dashboard-slot-settings-v1";
let availableModules = [];
let currentTheme = null;
let slotSettings = readSettings();

function readSettings() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    return value && typeof value === "object" && !Array.isArray(value)
      ? value : {};
  } catch (_) {
    return {};
  }
}

function saveSettings() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(slotSettings));
    statusText.textContent = "Selection saved in this browser";
  } catch (_) {
    statusText.textContent = "Browser storage unavailable; changes may not persist";
  }
}

function settingsFor(slotId) {
  if (!slotSettings[slotId] || typeof slotSettings[slotId] !== "object") {
    slotSettings[slotId] = { module: "empty", note: "" };
  }
  const setting = slotSettings[slotId];
  if (!availableModules.some(module => module.id === setting.module)) {
    setting.module = "empty";
  }
  if (typeof setting.note !== "string") setting.note = "";
  return setting;
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function renderModuleContent(body, slot, moduleId) {
  body.replaceChildren();
  const module = availableModules.find(item => item.id === moduleId);

  if (!module) {
    body.append(makeElement("div", "module-title", "Unknown module"));
    return;
  }

  if (moduleId === "empty") {
    body.append(
      makeElement("div", "empty", "Empty slot"),
      makeElement("div", "module-detail", module.description)
    );
    return;
  }

  if (moduleId === "dashboard-health") {
    body.append(
      makeElement("div", "module-title", module.name),
      makeElement("div", "module-detail", "Checking service health…")
    );
    const detail = body.lastElementChild;

    fetch("/health")
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(data => {
        detail.textContent = `${data.service}: ${data.status}`;
        detail.className = "module-status";
      })
      .catch(error => {
        detail.textContent = `Health check failed: ${error.message}`;
      });
    return;
  }

  if (moduleId === "theme-summary") {
    body.append(
      makeElement("div", "module-title", module.name),
      makeElement("div", "module-detail", `Theme: ${currentTheme.name}`),
      makeElement("div", "module-detail", `Slots: ${currentTheme.slots.length}`),
      makeElement("div", "module-detail", `Grid columns: ${currentTheme.grid.columns}`)
    );
    return;
  }

  if (moduleId === "slot-note") {
    const setting = settingsFor(slot.id);
    body.append(makeElement("div", "module-title", module.name));
    body.append(makeElement("div", "module-detail", module.description));

    const textarea = makeElement("textarea", "module-note-input");
    textarea.setAttribute("aria-label", `Note for ${slot.name || slot.id}`);
    textarea.placeholder = "Write a note for this slot…";
    textarea.value = setting.note;
    textarea.addEventListener("input", () => {
      settingsFor(slot.id).note = textarea.value;
      saveSettings();
    });
    body.append(textarea);
  }
}

function makeSlot(slot) {
  const card = makeElement("article", "slot");
  card.dataset.slotId = slot.id;
  card.style.gridColumn = `${slot.column} / span ${slot.column_span}`;
  card.style.gridRow = `${slot.row} / span ${slot.row_span}`;

  const head = makeElement("div", "slot-head");
  head.append(
    makeElement("div", "slot-name", slot.name || slot.id),
    makeElement("div", "slot-index", slot.id)
  );

  const controls = makeElement("div", "slot-controls");
  const label = makeElement("label", "", "Module");
  const select = makeElement("select", "module-select");
  select.setAttribute("aria-label", `Module for ${slot.name || slot.id}`);

  availableModules.forEach(module => {
    const option = makeElement("option", "", module.name);
    option.value = module.id;
    select.append(option);
  });

  const setting = settingsFor(slot.id);
  select.value = setting.module;

  const body = makeElement("div", "module-body");
  select.addEventListener("change", () => {
    settingsFor(slot.id).module = select.value;
    saveSettings();
    renderModuleContent(body, slot, select.value);
  });

  label.append(select);
  controls.append(label);
  card.append(head, controls, body);
  renderModuleContent(body, slot, select.value);
  return card;
}

async function loadTheme(themeId) {
  statusText.textContent = "Loading theme…";
  try {
    const response = await fetch(`/api/themes/${encodeURIComponent(themeId)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const theme = await response.json();

    currentTheme = theme;
    grid.replaceChildren();
    grid.style.setProperty("--theme-columns", theme.grid.columns);
    theme.slots.forEach(slot => grid.append(makeSlot(slot)));

    themeInfo.textContent =
      `${theme.name} · ${theme.slots.length} slots · ${theme.grid.columns} columns`;
    statusText.textContent = "Theme loaded · slot settings restored";
  } catch (error) {
    statusText.textContent = `Could not load theme: ${error.message}`;
  }
}

async function start() {
  try {
    const [themeResponse, moduleResponse] = await Promise.all([
      fetch("/api/themes"),
      fetch("/api/modules")
    ]);

    if (!themeResponse.ok) throw new Error(`Themes API: HTTP ${themeResponse.status}`);
    if (!moduleResponse.ok) throw new Error(`Modules API: HTTP ${moduleResponse.status}`);

    const themeData = await themeResponse.json();
    const moduleData = await moduleResponse.json();
    availableModules = moduleData.modules;

    themeSelect.replaceChildren();
    themeData.themes.forEach(theme => {
      const option = makeElement("option", "", `${theme.name} (${theme.slot_count})`);
      option.value = theme.id;
      themeSelect.append(option);
    });

    if (!themeData.themes.length) {
      statusText.textContent = "No theme files found";
      return;
    }

    const THEME_STORAGE_KEY = "xauusd-dashboard-active-theme-v1";
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const validTheme = themeData.themes.some(theme => theme.id === savedTheme);

    themeSelect.value = validTheme ? savedTheme : themeData.themes[0].id;

    themeSelect.addEventListener("change", () => {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, themeSelect.value);
      } catch (_) {
        statusText.textContent = "Theme could not be saved in this browser";
      }
      loadTheme(themeSelect.value);
    });

    await loadTheme(themeSelect.value);
  } catch (error) {
    statusText.textContent = `Startup failed: ${error.message}`;
  }
}

start();
</script>
</body>
</html>
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from flask import Flask, jsonify, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-key"

DATA_FILE = "archive_data.json"

INITIAL_FILE_DETAILS = {
    "Finch": """[ACCESS: O.DEPTHS // PERSONNEL FILE: FINCH]
[CLASSIFICATION LEVEL: INTERNAL // ACTIVE OPERATIVE]

──────────────────────────────────────────────
PERSONNEL DESIGNATION: “FINCH”
REAL NAME: RENATA HOLTZ
DIVISION: Surveillance / Aerial Drone Recon

──────────────────────────────────────────────
APPEARANCE
──────────────────────────────────────────────
Height: 1.60 m
Build: Compact, athletic
Hair: Black with streaks of white
Eyes: Amber
Distinguishing Marks: Silver implant line beneath right temple

──────────────────────────────────────────────
PERSONALITY
──────────────────────────────────────────────
Highly energetic, quick-witted, with a short attention span offset by hyper-focus during missions. Talks to her drones as though they were pets. Known for dark humor and improvisation under pressure.

──────────────────────────────────────────────
ANOMALOUS TRAIT
──────────────────────────────────────────────
Neural uplink enhancement — maintains direct sensory feed from multiple reconnaissance drones without delay. Capable of simultaneous visual tracking across 360° of airspace.

──────────────────────────────────────────────
NOTES
──────────────────────────────────────────────
Acts as live overwatch during extraction or suppression events. Known for recording extra “unofficial” footage of anomalies for personal analysis.
Psych evaluation: borderline obsession with flight analogies.""",
    "Gray": """[ACCESS: O.DEPTHS // PERSONNEL FILE: GRAY]
[CLASSIFICATION LEVEL: INTERNAL // ACTIVE OPERATIVE]

──────────────────────────────────────────────
PERSONNEL DESIGNATION: “GRAY”
REAL NAME: SAMUEL T. REESE
DIVISION: Infiltration / Shadow Containment

──────────────────────────────────────────────
APPEARANCE
──────────────────────────────────────────────
Height: 1.80 m
Build: Lithe, almost spectral physique
Hair: Silver-grey, short
Eyes: Pale blue, reflective under low light
Distinguishing Marks: Thin scar over left eyebrow

──────────────────────────────────────────────
PERSONALITY
──────────────────────────────────────────────
Soft-spoken, patient, borderline expressionless.
Prefers to work alone or with the entity AE-904 “Shadow-Walker.” The two have been recorded patrolling together during night shifts.

──────────────────────────────────────────────
ANOMALOUS TRAIT
──────────────────────────────────────────────
Partial “Shadow Echo” — can project a faint afterimage of himself for several seconds to confuse entities or surveillance systems. Theory suggests AE-904 may have “gifted” this to him unintentionally.

──────────────────────────────────────────────
NOTES
──────────────────────────────────────────────
Gray’s performance in low-visibility operations has led to unofficial designation as “Shadow Division liaison.”
When asked about AE-904, his only comment: “It’s like working with your reflection — but smarter.”""",
    "Stray": """[ACCESS: O.DEPTHS // PERSONNEL FILE: STRAY]
[CLASSIFICATION LEVEL: INTERNAL // ACTIVE OPERATIVE]

──────────────────────────────────────────────
PERSONNEL DESIGNATION: “STRAY”
REAL NAME: UNKNOWN
DIVISION: Field Reconnaissance / Unregistered Zone Scouting

──────────────────────────────────────────────
APPEARANCE
──────────────────────────────────────────────
Height: 1.76 m
Build: Lean, wiry musculature
Hair: Messy ash-blond, shoulder length
Eyes: Steel grey
Distinguishing Marks: Burn scar around neck partially covered by scarf

──────────────────────────────────────────────
PERSONALITY
──────────────────────────────────────────────
Detached but observant. Operates best when unsupervised. Often vanishes from radio contact for hours, reappearing with fully documented reports. Describes themself as “a finder, not a fighter.”
Prefers direct field observation to surveillance drones. Shows strong empathy toward entities with “misplaced purpose.”

──────────────────────────────────────────────
ANOMALOUS TRAIT
──────────────────────────────────────────────
Displays a subtle directional intuition — can locate any person, object, or exit once exposed to its trace for more than a few seconds. No compass or GPS needed. Trait possibly minor pre-cognitohazard.

──────────────────────────────────────────────
NOTES
──────────────────────────────────────────────
Operates with minimal supervision. Considered “half-feral” by some peers but holds a perfect recovery record for lost teams.
Commonly assigned to wilderness extractions and fog anomalies.""",
    "Violet": """[ACCESS: O.DEPTHS // PERSONNEL FILE: VIOLET]
[CLASSIFICATION LEVEL: INTERNAL // ACTIVE OPERATIVE]

──────────────────────────────────────────────
PERSONNEL DESIGNATION: “VIOLET”
REAL NAME: MARISSA CORDEL
DIVISION: Field Medical & Containment Support

──────────────────────────────────────────────
APPEARANCE
──────────────────────────────────────────────
Height: 1.68 m
Build: Slender
Hair: Deep auburn, tied in short braid
Eyes: Bright violet (confirmed natural anomaly pigmentation)
Identifying Features: Right wrist tattoo — geometric sigil (purpose unknown)

──────────────────────────────────────────────
PERSONALITY
──────────────────────────────────────────────
Calm, empathic, and methodical. Known for her unusual composure under duress. Considered the “moral compass” of her unit.
Has a habit of humming in empty hallways — audio recordings show the tune shifts to counteract ambient resonances from nearby anomalies.

──────────────────────────────────────────────
ANOMALOUS TRAIT
──────────────────────────────────────────────
“Resonant Harmony” — Violet can hum or speak in frequencies that stabilize localized cognitohazard exposure for short durations, reducing mental degradation among nearby personnel.

──────────────────────────────────────────────
NOTES
──────────────────────────────────────────────
Psychological screening: clear.
Frequently accompanies suppression teams into symbol-affected zones to neutralize exposure effects. Considered an indispensable support asset.""",
    "Ward": """[ACCESS: O.DEPTHS // PERSONNEL FILE: WARD]
[CLASSIFICATION LEVEL: INTERNAL // ACTIVE OPERATIVE]

──────────────────────────────────────────────
PERSONNEL DESIGNATION: “WARD”
REAL NAME: JONATHAN R. ELLIS
DIVISION: Containment Logistics / Equipment Specialist

──────────────────────────────────────────────
APPEARANCE
──────────────────────────────────────────────
Height: 1.89 m
Build: Heavy-set, broad-shouldered
Hair: Shaved close
Eyes: Hazel
Distinguishing Marks: Burn scars on forearms; mechanical brace on left knee

──────────────────────────────────────────────
PERSONALITY
──────────────────────────────────────────────
Gruff but protective. Described as the “field’s big brother.”
Highly loyal to team members, will prioritize human lives over containment unless directly countermanded.
Tends to keep sentimental trinkets from operations, each tagged and cataloged personally.

──────────────────────────────────────────────
ANOMALOUS TRAIT
──────────────────────────────────────────────
None verified. However, Ward displays unnatural resistance to gravitational compression fields, potentially due to prolonged exposure to AE-class anomalies.

──────────────────────────────────────────────
NOTES
──────────────────────────────────────────────
Specializes in rapid-deploy containment constructs and portable null-field emitters.
Instrumental in multiple high-risk capture operations; notable for carrying a reinforced pack containing modular containment anchors.""",
}

INITIAL_DATABASES = {
    "TOA": {
        "Agent Files": {
            "icon": "Fingerprint",
            "subdivisions": {
                "Field Agents": ["Finch", "Gray", "Shard", "Stray", "Violet", "Ward"],
                "Researchers": ["Glassmind", "Restorer", "Scribe", "Semioticion", "Synthetist"],
            },
            "files": [],
        },
        "Compendium of the Archives": {
            "icon": "Database",
            "subdivisions": {
                "Logo": [],
                "Verified Resources": ["Object Classifications"],
            },
            "files": [],
        },
        "Entities": {
            "icon": "ShieldAlert",
            "subdivisions": {
                "Ecliptic": ["AE-352"],
                "First Discovered": ["AE-331", "AE-332", "AE-412-A/B", "AE-777", "AE-920"],
                "Newly Discovered": ["AE-175", "AE-214", "AE-909", "AE-911", "AE-923"],
                "Shadow": ["AE-889", "AE-913", "AE-914", "AE-915"],
                "Symbol": ["AE-072", "AE-702"],
                "Kenopses": [
                    "AE-L0", "AE-L1", "AE-L2", "AE-L4", "AE-L7", "AE-L10",
                    "AE-L15", "AE-L18", "AE-L22", "AE-L23", "AE-L29",
                    "AE-L31", "AE-L48",
                ],
                "Triptych": ["AE-000", "AE-601", "AE-602", "AE-603"],
            },
            "files": [],
        },
        "Incident Reports": {
            "icon": "AlertTriangle",
            "subdivisions": {
                "Incident-01": [],
            },
            "files": [],
        },
        "Mission Reports": {
            "icon": "Crosshair",
            "subdivisions": {
                "Mission Report-01": [],
            },
            "files": [],
        },
    },
    "BV": {
        "BV Root Files": {
            "icon": "Database",
            "subdivisions": {
                "Echo-Walker Logs": ["Log-01", "Log-02"],
                "Encrypted Nodes": ["Node-Alpha", "Node-Beta"],
            },
            "files": [],
        },
        "Projects": {
            "icon": "Folder",
            "subdivisions": {
                "Active": ["Project-Omega"],
                "Suspended": ["Project-Icarus"],
            },
            "files": [],
        },
    },
}

DEFAULT_DATA = {
    "databases": INITIAL_DATABASES,
    "customNotes": {},
    "fileContents": INITIAL_FILE_DETAILS,
}


def load_data() -> dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        save_data(deepcopy(DEFAULT_DATA))
        return deepcopy(DEFAULT_DATA)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (json.JSONDecodeError, OSError):
        loaded = deepcopy(DEFAULT_DATA)

    for k, v in DEFAULT_DATA.items():
        if k not in loaded:
            loaded[k] = deepcopy(v)

    return loaded


def save_data(data: dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def logged_in() -> bool:
    return bool(session.get("authenticated"))


def is_admin() -> bool:
    return bool(session.get("is_admin"))


def require_login():
    if not logged_in():
        return jsonify({"ok": False, "error": "Not authenticated"}), 401
    return None


def require_admin():
    if not logged_in():
        return jsonify({"ok": False, "error": "Not authenticated"}), 401
    if not is_admin():
        return jsonify({"ok": False, "error": "Admin access required"}), 403
    return None


def ensure_file_content(data: dict[str, Any], file_name: str) -> None:
    if file_name not in data["fileContents"]:
        data["fileContents"][file_name] = (
            f"[FILE: {file_name}]\n\nNo archived text currently exists for this file."
        )


HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Archive Terminal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;800;900&display=swap');

    :root{
      --bg:#05060d;
      --panel:#0d1020;
      --panel2:#12172b;
      --border:#8e66ff;
      --border-soft:#4d3798;
      --text:#c7a8ff;
      --text-bright:#e6d8ff;
      --muted:#aa89ec;
      --danger:#ff6887;
      --success:#8affc1;
      --accent:#a97cff;
      --hover:#1a2040;
      --glow:0 0 10px rgba(169,124,255,.35), 0 0 20px rgba(169,124,255,.16);
    }

    *{
      box-sizing:border-box;
      font-family:'Orbitron', sans-serif !important;
      font-weight:800 !important;
      color:var(--text);
    }

    body{
      margin:0;
      background:
        radial-gradient(circle at top, rgba(160,110,255,.12), transparent 35%),
        linear-gradient(180deg,#03040a 0%,#080b14 100%);
    }

    .wrap{max-width:1300px;margin:0 auto;padding:18px}
    .card{
      background:rgba(13,16,32,.94);
      border:1px solid var(--border-soft);
      border-radius:14px;
      box-shadow:0 0 0 1px rgba(166,121,255,.08), 0 0 28px rgba(109,69,214,.20);
    }

    .login-wrap{
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:20px;
    }

    .login-card{
      width:100%;
      max-width:460px;
      padding:24px;
    }

    h1,h2,h3,p{margin:0;color:var(--text-bright);text-shadow:var(--glow)}
    .title{font-size:30px;letter-spacing:2px}
    .sub{
      color:var(--muted);
      margin-top:8px;
      font-size:13px;
      text-shadow:0 0 8px rgba(169,124,255,.2);
    }

    .field{margin-top:18px}
    label{
      display:block;
      margin-bottom:8px;
      color:var(--muted);
      font-size:12px;
      text-transform:uppercase;
      letter-spacing:1.5px;
      text-shadow:0 0 8px rgba(169,124,255,.15);
    }

    input, textarea, select{
      width:100%;
      background:#090c18;
      color:var(--text-bright);
      border:1px solid var(--border-soft);
      border-radius:10px;
      padding:12px 14px;
      font-size:13px;
      outline:none;
      box-shadow:inset 0 0 10px rgba(140,90,255,.08);
    }

    input:focus, textarea:focus, select:focus{
      border-color:var(--border);
      box-shadow:0 0 0 1px rgba(166,121,255,.35), 0 0 14px rgba(166,121,255,.15);
    }

    textarea{resize:vertical}

    button{
      background:#1a2040;
      color:var(--text-bright);
      border:1px solid var(--border);
      border-radius:10px;
      padding:10px 14px;
      cursor:pointer;
      transition:.15s ease;
      text-shadow:var(--glow);
      box-shadow:0 0 12px rgba(166,121,255,.08);
    }

    button:hover{
      background:#252f5f;
      box-shadow:0 0 14px rgba(166,121,255,.18);
      transform:translateY(-1px);
    }

    button.danger{
      border-color:rgba(255,104,135,.55);
      color:#ffd8e1;
      background:#2b1620;
      text-shadow:0 0 10px rgba(255,104,135,.2);
    }

    button.danger:hover{background:#3b1c28}
    button.ghost{background:transparent;border-color:var(--border-soft)}
    .full{width:100%}

    .topbar{
      display:flex;
      gap:12px;
      justify-content:space-between;
      align-items:flex-start;
      padding-bottom:14px;
      border-bottom:1px solid var(--border-soft);
      margin-bottom:18px;
      flex-wrap:wrap;
    }

    .status{
      display:grid;
      grid-template-columns:1fr 2fr;
      gap:8px 14px;
      font-size:13px;
      color:var(--muted);
    }

    .status strong{color:var(--text-bright);text-shadow:var(--glow)}
    .layout{display:grid;grid-template-columns:330px 1fr;gap:18px}
    .panel{padding:16px}
    .header-row{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
    .tree-section{border-top:1px solid rgba(154,124,255,.15);padding-top:10px;margin-top:10px}

    .category{
      border:1px solid rgba(154,124,255,.16);
      border-radius:12px;
      margin-bottom:12px;
      overflow:hidden;
      background:rgba(255,255,255,.01);
    }

    .cat-header,.sub-header,.file-row{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
    }

    .cat-header{
      padding:12px 14px;
      background:rgba(154,124,255,.05);
    }

    .cat-header:hover,.sub-header:hover,.file-row:hover{background:var(--hover)}

    .cat-left,.sub-left,.file-left{
      display:flex;
      align-items:center;
      gap:10px;
      min-width:0;
      flex:1;
      cursor:pointer;
    }

    .cat-actions,.sub-actions,.file-actions{
      display:flex;
      gap:6px;
      flex-shrink:0;
    }

    .mini{
      padding:5px 8px;
      font-size:11px;
      border-radius:8px;
    }

    .cat-body{display:none;padding:10px 12px 12px 12px}
    .cat-body.open{display:block}

    .subbox{
      border:1px solid rgba(154,124,255,.12);
      border-radius:10px;
      margin-top:8px;
      overflow:hidden;
    }

    .sub-header{padding:9px 12px}
    .sub-body{display:none;padding:8px 10px 10px 18px;border-top:1px solid rgba(154,124,255,.12)}
    .sub-body.open{display:block}

    .file-row{
      padding:8px 10px;
      border-radius:8px;
      margin-top:4px;
      color:var(--text-bright);
    }

    .muted{color:var(--muted)}
    .badge{
      display:inline-block;
      border:1px solid rgba(138,255,193,.35);
      color:var(--success);
      padding:2px 8px;
      border-radius:999px;
      font-size:10px;
      text-shadow:0 0 8px rgba(138,255,193,.2);
    }

    .dialog-backdrop{
      position:fixed;
      inset:0;
      background:rgba(0,0,0,.66);
      display:none;
      align-items:center;
      justify-content:center;
      padding:20px;
      z-index:50;
    }

    .dialog-backdrop.open{display:flex}
    .dialog{
      width:min(1050px, 96vw);
      max-height:88vh;
      overflow:auto;
      padding:16px;
    }

    .split{display:grid;grid-template-columns:1fr;gap:14px}
    .box{
      border:1px solid rgba(154,124,255,.15);
      border-radius:12px;
      padding:14px;
      background:rgba(255,255,255,.02);
    }

    .box-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
    pre{
      white-space:pre-wrap;
      word-break:break-word;
      color:var(--text-bright);
      margin:0;
      line-height:1.5;
      text-shadow:0 0 8px rgba(169,124,255,.12);
    }

    .row{display:flex;gap:10px;flex-wrap:wrap}
    .notice{
      margin-top:12px;
      font-size:13px;
      color:var(--muted);
      min-height:18px;
      text-shadow:0 0 8px rgba(169,124,255,.15);
    }

    @media (max-width: 900px){
      .layout{grid-template-columns:1fr}
    }
  </style>
</head>
<body>
<div id="app"></div>

<script>
let state = {
  authenticated: false,
  is_admin: false,
  username: "",
  active_db: "TOA",
  databases: {},
  customNotes: {},
  fileContents: {},
  selectedFile: null,
  currentFileContent: "",
  currentEditNote: "",
  isEditingFile: false,
  categoryOpen: {},
  subdivisionOpen: {}
};

function esc(s){
  return String(s ?? "")
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;");
}

function attrEsc(s){
  return String(s ?? "")
    .replaceAll("&","&amp;")
    .replaceAll('"',"&quot;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;");
}

function notify(msg, isError=false){
  const el = document.getElementById("notice");
  if(!el) return;
  el.textContent = msg;
  el.style.color = isError ? "#ff9aae" : "#aa89ec";
}

async function api(path, method="GET", body=null){
  const opts = {method, headers:{}};
  if(body !== null){
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  const data = await res.json();
  if(!res.ok || data.ok === false){
    throw new Error(data.error || "Request failed");
  }
  return data;
}

async function loadState(){
  try{
    const data = await api("/api/state");
    state = {...state, ...data.state};
    render();
  }catch(err){
    document.getElementById("app").innerHTML =
      '<div class="login-wrap"><div class="card login-card"><h1 class="title">ERROR</h1><p class="sub">'+esc(err.message)+'</p></div></div>';
  }
}

async function refreshState(keepSelection=false){
  const selectedBefore = keepSelection ? state.selectedFile : null;
  const fileContentBefore = keepSelection ? state.currentFileContent : "";
  const noteBefore = keepSelection ? state.currentEditNote : "";
  const editingBefore = keepSelection ? state.isEditingFile : false;

  const data = await api("/api/state");
  state = {...state, ...data.state};

  if (keepSelection && selectedBefore) {
    state.selectedFile = selectedBefore;
    state.currentFileContent = fileContentBefore;
    state.currentEditNote = noteBefore;
    state.isEditingFile = editingBefore;
  }

  render();
}

function toggleCategory(name){
  state.categoryOpen[name] = !state.categoryOpen[name];
  render();
}

function toggleSubdivision(cat, sub){
  const key = cat + "||" + sub;
  state.subdivisionOpen[key] = !state.subdivisionOpen[key];
  render();
}

async function login(e){
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try{
    const data = await api("/api/login", "POST", {username, password});
    state = {...state, ...data.state};
    render();
    notify(data.message || "Access granted");
  }catch(err){
    notify(err.message, true);
  }
}

async function logout(){
  try{
    const data = await api("/api/logout", "POST", {});
    state = {...state, ...data.state};
    render();
    notify(data.message || "Logged out");
  }catch(err){
    notify(err.message, true);
  }
}

async function switchDb(){
  try{
    const nextDb = state.active_db === "TOA" ? "BV" : "TOA";
    const data = await api("/api/switch_db", "POST", {active_db: nextDb});
    state = {...state, ...data.state};
    state.selectedFile = null;
    state.currentFileContent = "";
    state.currentEditNote = "";
    state.isEditingFile = false;
    render();
  }catch(err){
    notify(err.message, true);
  }
}

async function openFile(fileName){
  try{
    const data = await api("/api/file/" + encodeURIComponent(fileName));
    state.selectedFile = fileName;
    state.currentFileContent = data.file_content;
    state.currentEditNote = data.note;
    state.isEditingFile = false;
    render();
  }catch(err){
    notify(err.message, true);
  }
}

function closeDialog(){
  state.selectedFile = null;
  state.currentFileContent = "";
  state.currentEditNote = "";
  state.isEditingFile = false;
  render();
}

async function saveFileContent(){
  try{
    await api("/api/file/" + encodeURIComponent(state.selectedFile) + "/content", "POST", {
      content: state.currentFileContent
    });
    await openFile(state.selectedFile);
    notify("Core file overwritten");
  }catch(err){
    notify(err.message, true);
  }
}

async function saveAdminNote(){
  try{
    await api("/api/file/" + encodeURIComponent(state.selectedFile) + "/note", "POST", {
      note: state.currentEditNote
    });
    await openFile(state.selectedFile);
    notify("Admin note saved");
  }catch(err){
    notify(err.message, true);
  }
}

async function addEntry(){
  const type = prompt("What would you like to add?\n1. Category\n2. Subdivision\n3. File\nEnter 1, 2, or 3:");
  if(!type) return;

  if(type === "1"){
    const category = prompt("Enter new Category name:");
    if(!category) return;
    try{
      await api("/api/add/category", "POST", {category});
      await refreshState();
    }catch(err){ notify(err.message, true); }
    return;
  }

  if(type === "2"){
    const categories = Object.keys(state.databases[state.active_db] || {});
    if(categories.length === 0){ alert("Please create a Category first."); return; }
    const catList = categories.map((c,i)=>`${i+1}. ${c}`).join("\n");
    const catIndexStr = prompt(`Select a Category to add to (enter number):\n${catList}`);
    if(!catIndexStr) return;
    const catIndex = parseInt(catIndexStr, 10) - 1;
    const catName = categories[catIndex];
    if(!catName){ alert("Invalid category selection."); return; }
    const subdivision = prompt(`Enter new Subdivision name for ${catName}:`);
    if(!subdivision) return;
    try{
      await api("/api/add/subdivision", "POST", {category: catName, subdivision});
      state.categoryOpen[catName] = true;
      await refreshState();
    }catch(err){ notify(err.message, true); }
    return;
  }

  if(type === "3"){
    const categories = Object.keys(state.databases[state.active_db] || {});
    if(categories.length === 0){ alert("Please create a Category first."); return; }
    const catList = categories.map((c,i)=>`${i+1}. ${c}`).join("\n");
    const catIndexStr = prompt(`Select a Category to add to (enter number):\n${catList}`);
    if(!catIndexStr) return;
    const catIndex = parseInt(catIndexStr, 10) - 1;
    const catName = categories[catIndex];
    if(!catName){ alert("Invalid category selection."); return; }

    const subdivisions = Object.keys((state.databases[state.active_db][catName] || {}).subdivisions || {});
    let subName = null;

    if(subdivisions.length === 0){
      const confirmNewSub = confirm(`No subdivisions found in ${catName}. Would you like to create one first? (Cancel adds directly to category)`);
      if(confirmNewSub){
        subName = prompt(`Enter new Subdivision name for ${catName}:`);
        if(!subName) return;
      }
    }else{
      const subList = ["0. None (Add directly to category)"];
      subdivisions.forEach((s,i)=>subList.push(`${i+1}. ${s}`));
      const subIndexStr = prompt(`Select a Subdivision in ${catName} (enter number):\n${subList.join("\n")}`);
      if(!subIndexStr) return;
      const subIndex = parseInt(subIndexStr, 10);
      if(subIndex !== 0){
        subName = subdivisions[subIndex - 1];
        if(!subName){ alert("Invalid subdivision selection."); return; }
      }
    }

    const fileName = prompt(`Enter new File name for ${catName}${subName ? " -> " + subName : ""}:`);
    if(!fileName) return;

    try{
      await api("/api/add/file", "POST", {category: catName, subdivision: subName, file_name: fileName});
      state.categoryOpen[catName] = true;
      if (subName) state.subdivisionOpen[catName + "||" + subName] = true;
      await refreshState();
    }catch(err){ notify(err.message, true); }
    return;
  }

  alert("Invalid selection. Please enter 1, 2, or 3.");
}

async function addSubdivisionOrFile(category){
  const type = prompt(`What would you like to add to ${category}?\n1. Subdivision\n2. File\nEnter 1 or 2:`);
  if(!type) return;

  if(type === "1"){
    const subdivision = prompt(`Enter new Subdivision name for ${category}:`);
    if(!subdivision) return;
    try{
      await api("/api/add/subdivision", "POST", {category, subdivision});
      state.categoryOpen[category] = true;
      await refreshState();
    }catch(err){ notify(err.message, true); }
    return;
  }

  if(type === "2"){
    const subdivisions = Object.keys((state.databases[state.active_db][category] || {}).subdivisions || {});
    let subName = null;

    if(subdivisions.length === 0){
      const confirmNewSub = confirm(`No subdivisions found in ${category}. Would you like to create one first? (Cancel adds directly to category)`);
      if(confirmNewSub){
        subName = prompt(`Enter new Subdivision name for ${category}:`);
        if(!subName) return;
      }
    }else{
      const subList = ["0. None (Add directly to category)"];
      subdivisions.forEach((s,i)=>subList.push(`${i+1}. ${s}`));
      const subIndexStr = prompt(`Select a Subdivision in ${category} to add the file to (enter number):\n${subList.join("\n")}`);
      if(!subIndexStr) return;
      const subIndex = parseInt(subIndexStr, 10);
      if(subIndex !== 0){
        subName = subdivisions[subIndex - 1];
        if(!subName){ alert("Invalid subdivision selection."); return; }
      }
    }

    const fileName = prompt(`Enter new File name for ${category}${subName ? " -> " + subName : ""}:`);
    if(!fileName) return;

    try{
      await api("/api/add/file", "POST", {category, subdivision: subName, file_name: fileName});
      state.categoryOpen[category] = true;
      if (subName) state.subdivisionOpen[category + "||" + subName] = true;
      await refreshState();
    }catch(err){ notify(err.message, true); }
    return;
  }

  alert("Invalid selection. Please enter 1 or 2.");
}

async function addFile(category, subdivision){
  const fileName = prompt("Enter new File name:");
  if(!fileName) return;

  try{
    await api("/api/add/file", "POST", {category, subdivision, file_name: fileName});
    state.categoryOpen[category] = true;
    state.subdivisionOpen[category + "||" + subdivision] = true;
    await refreshState();
  }catch(err){
    notify(err.message, true);
  }
}

async function removeCategory(category){
  if(!confirm(`Are you sure you want to delete category "${category}"?`)) return;
  try{
    await api("/api/delete/category", "POST", {category});
    if (state.selectedFile) closeDialog();
    delete state.categoryOpen[category];
    await refreshState();
  }catch(err){
    notify(err.message, true);
  }
}

async function removeSubdivision(category, subdivision){
  if(!confirm(`Are you sure you want to delete subdivision "${subdivision}"?`)) return;
  try{
    await api("/api/delete/subdivision", "POST", {category, subdivision});
    delete state.subdivisionOpen[category + "||" + subdivision];
    await refreshState();
  }catch(err){
    notify(err.message, true);
  }
}

async function removeFile(category, subdivision, fileName){
  if(!confirm(`Are you sure you want to delete file "${fileName}"?`)) return;
  try{
    await api("/api/delete/file", "POST", {category, subdivision, file_name: fileName});
    if(state.selectedFile === fileName){
      closeDialog();
    }
    await refreshState();
  }catch(err){
    notify(err.message, true);
  }
}

function renderLogin(){
  document.getElementById("app").innerHTML = `
    <div class="login-wrap">
      <div class="card login-card">
        <h1 class="title">RESTRICTED ACCESS</h1>
        <p class="sub">TERMINAL AUTHORIZATION REQUIRED</p>
        <form id="loginForm">
          <div class="field">
            <label>Operator ID</label>
            <input id="username" type="text" placeholder="ENTER OPERATOR ID">
          </div>
          <div class="field">
            <label>Passcode</label>
            <input id="password" type="password" placeholder="ENTER PASSCODE">
          </div>
          <div class="field">
            <button class="full" type="submit">INITIALIZE CONNECTION</button>
          </div>
          <div id="notice" class="notice"></div>
        </form>
      </div>
    </div>
  `;
  document.getElementById("loginForm").addEventListener("submit", login);
}

function renderMain(){
  const db = state.databases[state.active_db] || {};
  const isAdmin = state.is_admin;

  let categoriesHtml = "";
  for(const [category, data] of Object.entries(db)){
    const catOpen = !!state.categoryOpen[category];

    const directFiles = (data.files || []).map(file => `
      <div class="file-row">
        <div class="file-left" data-action="open-file" data-file="${attrEsc(file)}">
          <span>📄</span>
          <span>${esc(file)}</span>
          ${state.customNotes[file] && !isAdmin ? '<span class="badge">NOTE</span>' : ''}
        </div>
        ${isAdmin ? `
          <div class="file-actions">
            <button class="mini danger" data-action="delete-file" data-category="${attrEsc(category)}" data-file="${attrEsc(file)}">DEL</button>
          </div>
        ` : ""}
      </div>
    `).join("");

    const subdivisionsHtml = Object.entries(data.subdivisions || {}).map(([subdiv, files]) => {
      const key = category + "||" + subdiv;
      const subOpen = !!state.subdivisionOpen[key];
      const fileRows = (files || []).length > 0
        ? files.map(file => `
          <div class="file-row">
            <div class="file-left" data-action="open-file" data-file="${attrEsc(file)}">
              <span>📄</span>
              <span>${esc(file)}</span>
              ${state.customNotes[file] && !isAdmin ? '<span class="badge">NOTE</span>' : ''}
            </div>
            ${isAdmin ? `
              <div class="file-actions">
                <button class="mini danger" data-action="delete-file" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}" data-file="${attrEsc(file)}">DEL</button>
              </div>
            ` : ""}
          </div>
        `).join("")
        : `<div class="muted" style="padding:8px 10px;">NO FILES PRESENT.</div>`;

      return `
        <div class="subbox">
          <div class="sub-header">
            <div class="sub-left" data-action="toggle-subdivision" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}">
              <span>📁</span>
              <span>${esc(subdiv)}</span>
            </div>
            ${isAdmin ? `
              <div class="sub-actions">
                <button class="mini ghost" data-action="add-file" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}">ADD FILE</button>
                <button class="mini danger" data-action="delete-subdivision" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}">DEL SUB</button>
              </div>
            ` : ""}
          </div>
          <div class="sub-body ${subOpen ? "open" : ""}">
            ${fileRows}
          </div>
        </div>
      `;
    }).join("");

    categoriesHtml += `
      <div class="category">
        <div class="cat-header">
          <div class="cat-left" data-action="toggle-category" data-category="${attrEsc(category)}">
            <span>🗂</span>
            <span>${esc(category)}</span>
          </div>
          ${isAdmin ? `
            <div class="cat-actions">
              <button class="mini ghost" data-action="add-subdivision-or-file" data-category="${attrEsc(category)}">ADD</button>
              <button class="mini danger" data-action="delete-category" data-category="${attrEsc(category)}">DEL</button>
            </div>
          ` : ""}
        </div>
        <div class="cat-body ${catOpen ? "open" : ""}">
          ${directFiles}
          ${subdivisionsHtml}
        </div>
      </div>
    `;
  }

  const selected = state.selectedFile;
  const dialogOpen = !!selected;
  const noteVisible = isAdmin || (!!selected && !!state.customNotes[selected]);

  document.getElementById("app").innerHTML = `
    <div class="wrap">
      <div class="topbar">
        <div>
          <h1 class="title">${esc(state.active_db)}_TERMINAL</h1>
          <p class="sub">SECURE CONNECTION ESTABLISHED // ${isAdmin ? "ADMIN OVERRIDE ACTIVE" : "STANDARD OP LEVEL"}</p>
        </div>
        <div class="row">
          ${isAdmin ? `<button data-action="switch-db">SWITCH TO ${state.active_db === "TOA" ? "BV" : "TOA"}</button>` : ""}
          <button class="danger" data-action="logout">TERMINATE</button>
        </div>
      </div>

      <div class="layout">
        <div class="card panel">
          <div class="header-row">
            <h2>SYSTEM STATUS</h2>
          </div>
          <div class="status">
            <div>OPERATOR:</div><strong>${esc(isAdmin ? "ADMIN" : state.username)}</strong>
            <div>ACCESS LEVEL:</div><strong>${esc(isAdmin ? "OMEGA-PRIME" : "OMEGA")}</strong>
            <div>ENCRYPTION:</div><strong>256-BIT QUANTUM</strong>
            <div>DATABASE SYNC:</div><strong>100%</strong>
            <div>ACTIVE NODE:</div><strong>${esc(state.active_db)} ROOT</strong>
          </div>
        </div>

        <div class="card panel">
          <div class="header-row">
            <div>
              <h2>MAIN_DIRECTORY</h2>
              <p class="sub">NAVIGATE THE ARCHIVAL RECORDS BELOW.</p>
            </div>
            ${isAdmin ? `<button data-action="add-entry">ADD ENTRY</button>` : ""}
          </div>

          <div class="tree-section">
            ${categoriesHtml || '<div class="muted">NO CATEGORIES AVAILABLE.</div>'}
          </div>
        </div>
      </div>

      <div id="notice" class="notice"></div>
    </div>

    <div class="dialog-backdrop ${dialogOpen ? "open" : ""}" id="dialogBackdrop">
      <div class="card dialog">
        <div class="header-row">
          <h2>📄 ${esc(selected || "")}</h2>
          <button class="ghost" data-action="close-dialog">CLOSE</button>
        </div>

        <div class="split">
          <div class="box">
            <div class="box-head">
              <h3>CORE FILE</h3>
              ${isAdmin ? `
                <div class="row">
                  ${
                    state.isEditingFile
                    ? `
                      <button data-action="save-file">SAVE</button>
                      <button class="danger" data-action="cancel-edit">CANCEL</button>
                    `
                    : `<button data-action="start-edit">EDIT</button>`
                  }
                </div>
              ` : ""}
            </div>

            ${
              isAdmin && state.isEditingFile
              ? `<textarea id="fileContentEditor" style="min-height:340px;">${esc(state.currentFileContent || "")}</textarea>`
              : `<pre>${esc(state.currentFileContent || "")}</pre>`
            }
          </div>

          ${noteVisible ? `
            <div class="box">
              <div class="box-head">
                <h3>ADMIN NOTES</h3>
                ${isAdmin ? `<button data-action="save-note">SAVE NOTE</button>` : ""}
              </div>
              ${
                isAdmin
                ? `<textarea id="noteEditor" style="min-height:180px;">${esc(state.currentEditNote || "")}</textarea>`
                : `<pre>${esc((selected && state.customNotes[selected]) || "")}</pre>`
              }
            </div>
          ` : ""}
        </div>
      </div>
    </div>
  `;

  wireMainEvents();

  if (isAdmin && state.isEditingFile) {
    const ed = document.getElementById("fileContentEditor");
    if (ed) {
      ed.addEventListener("input", (e) => {
        state.currentFileContent = e.target.value;
      });
    }
  }

  if (isAdmin && dialogOpen) {
    const noteEd = document.getElementById("noteEditor");
    if (noteEd) {
      noteEd.addEventListener("input", (e) => {
        state.currentEditNote = e.target.value;
      });
    }
  }

  const backdrop = document.getElementById("dialogBackdrop");
  if (backdrop) {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) closeDialog();
    });
  }
}

function wireMainEvents(){
  document.querySelectorAll("[data-action]").forEach((el) => {
    el.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const action = el.dataset.action;

      if (action === "logout") return logout();
      if (action === "switch-db") return switchDb();
      if (action === "add-entry") return addEntry();
      if (action === "close-dialog") return closeDialog();

      if (action === "toggle-category") return toggleCategory(el.dataset.category);
      if (action === "toggle-subdivision") return toggleSubdivision(el.dataset.category, el.dataset.subdivision);
      if (action === "open-file") return openFile(el.dataset.file);

      if (action === "add-subdivision-or-file") return addSubdivisionOrFile(el.dataset.category);
      if (action === "delete-category") return removeCategory(el.dataset.category);
      if (action === "add-file") return addFile(el.dataset.category, el.dataset.subdivision);
      if (action === "delete-subdivision") return removeSubdivision(el.dataset.category, el.dataset.subdivision);
      if (action === "delete-file") return removeFile(el.dataset.category, el.dataset.subdivision || null, el.dataset.file);

      if (action === "start-edit") {
        state.isEditingFile = true;
        render();
        return;
      }

      if (action === "cancel-edit") {
        if (state.selectedFile) {
          return openFile(state.selectedFile);
        }
        state.isEditingFile = false;
        render();
        return;
      }

      if (action === "save-file") return saveFileContent();
      if (action === "save-note") return saveAdminNote();
    });
  });
}

function render(){
  if(!state.authenticated){
    renderLogin();
  }else{
    renderMain();
  }
}

loadState();
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(HTML)


@app.get("/api/state")
def api_state():
    data = load_data()
    return jsonify({
        "ok": True,
        "state": {
            "authenticated": logged_in(),
            "is_admin": is_admin(),
            "username": session.get("username", ""),
            "active_db": session.get("active_db", "TOA"),
            "databases": data["databases"],
            "customNotes": data["customNotes"],
            "fileContents": data["fileContents"],
        }
    })


@app.post("/api/login")
def api_login():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "")
    password = body.get("password", "")

    if username == "ADMIN" and password == "TheWraith!13":
        session["authenticated"] = True
        session["is_admin"] = True
        session["username"] = username
        session["active_db"] = "TOA"
        msg = "ADMINISTRATIVE ACCESS GRANTED"
    elif username == "TOA Terminal" and password == "Paer-X":
        session["authenticated"] = True
        session["is_admin"] = False
        session["username"] = username
        session["active_db"] = "TOA"
        msg = "ACCESS GRANTED: TOA"
    elif username == "BV Terminal" and password == "Echo-Walker":
        session["authenticated"] = True
        session["is_admin"] = False
        session["username"] = username
        session["active_db"] = "BV"
        msg = "ACCESS GRANTED: BV"
    else:
        return jsonify({"ok": False, "error": "ACCESS DENIED: INVALID CREDENTIALS"}), 401

    data = load_data()
    return jsonify({
        "ok": True,
        "message": msg,
        "state": {
            "authenticated": True,
            "is_admin": session["is_admin"],
            "username": session["username"],
            "active_db": session["active_db"],
            "databases": data["databases"],
            "customNotes": data["customNotes"],
            "fileContents": data["fileContents"],
        }
    })


@app.post("/api/logout")
def api_logout():
    session.clear()
    data = load_data()
    return jsonify({
        "ok": True,
        "message": "SYSTEM LOGOUT",
        "state": {
            "authenticated": False,
            "is_admin": False,
            "username": "",
            "active_db": "TOA",
            "databases": data["databases"],
            "customNotes": data["customNotes"],
            "fileContents": data["fileContents"],
        }
    })


@app.post("/api/switch_db")
def api_switch_db():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    active_db = body.get("active_db", "TOA")
    if active_db not in ("TOA", "BV"):
        return jsonify({"ok": False, "error": "INVALID DATABASE"}), 400

    session["active_db"] = active_db
    data = load_data()
    return jsonify({
        "ok": True,
        "state": {
            "authenticated": True,
            "is_admin": True,
            "username": session.get("username", "ADMIN"),
            "active_db": active_db,
            "databases": data["databases"],
            "customNotes": data["customNotes"],
            "fileContents": data["fileContents"],
        }
    })


@app.get("/api/file/<path:file_name>")
def api_get_file(file_name: str):
    auth_err = require_login()
    if auth_err:
        return auth_err

    data = load_data()
    ensure_file_content(data, file_name)
    save_data(data)

    return jsonify({
        "ok": True,
        "file_name": file_name,
        "file_content": data["fileContents"].get(
            file_name,
            f"[FILE: {file_name}]\n\nNo archived text currently exists for this file."
        ),
        "note": data["customNotes"].get(file_name, ""),
    })


@app.post("/api/file/<path:file_name>/content")
def api_set_file_content(file_name: str):
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    content = body.get("content", "")

    data = load_data()
    data["fileContents"][file_name] = content
    save_data(data)

    return jsonify({"ok": True})


@app.post("/api/file/<path:file_name>/note")
def api_set_file_note(file_name: str):
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    note = body.get("note", "")

    data = load_data()
    data["customNotes"][file_name] = note
    save_data(data)

    return jsonify({"ok": True})


@app.post("/api/add/category")
def api_add_category():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    if not category:
        return jsonify({"ok": False, "error": "MISSING CATEGORY"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    data["databases"][active_db][category] = {
        "icon": "Folder",
        "subdivisions": {},
        "files": [],
    }
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/add/subdivision")
def api_add_subdivision():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    subdivision = body.get("subdivision", "").strip()

    if not category or not subdivision:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR SUBDIVISION"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    db = data["databases"][active_db]
    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404

    db[category].setdefault("subdivisions", {})
    db[category]["subdivisions"][subdivision] = []
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/add/file")
def api_add_file():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    subdivision = body.get("subdivision")
    file_name = body.get("file_name", "").strip()

    if not category or not file_name:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR FILE NAME"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    db = data["databases"][active_db]

    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404

    ensure_file_content(data, file_name)

    if subdivision:
        db[category].setdefault("subdivisions", {})
        db[category]["subdivisions"].setdefault(subdivision, [])
        db[category]["subdivisions"][subdivision].append(file_name)
    else:
        db[category].setdefault("files", [])
        db[category]["files"].append(file_name)

    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/category")
def api_delete_category():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    if not category:
        return jsonify({"ok": False, "error": "MISSING CATEGORY"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    data["databases"][active_db].pop(category, None)
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/subdivision")
def api_delete_subdivision():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    subdivision = body.get("subdivision", "").strip()

    if not category or not subdivision:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR SUBDIVISION"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    db = data["databases"][active_db]

    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404

    db[category].setdefault("subdivisions", {})
    db[category]["subdivisions"].pop(subdivision, None)
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/file")
def api_delete_file():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    subdivision = body.get("subdivision")
    file_name = body.get("file_name", "").strip()

    if not category or not file_name:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR FILE NAME"}), 400

    data = load_data()
    active_db = session.get("active_db", "TOA")
    db = data["databases"][active_db]

    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404

    if subdivision:
        db[category].setdefault("subdivisions", {})
        files = db[category]["subdivisions"].get(subdivision, [])
        db[category]["subdivisions"][subdivision] = [f for f in files if f != file_name]
    else:
        files = db[category].get("files", [])
        db[category]["files"] = [f for f in files if f != file_name]

    save_data(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from flask import Flask, jsonify, render_template_string, request, session
from werkzeug.security import check_password_hash, generate_password_hash

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
                    "AE-L15", "AE-L18", "AE-L22", "AE-L23", "AE-L29", "AE-L31", "AE-L48",
                ],
                "Triptych": ["AE-000", "AE-601", "AE-602", "AE-603"],
            },
            "files": [],
        },
        "Incident Reports": {
            "icon": "AlertTriangle",
            "subdivisions": {"Incident-01": []},
            "files": [],
        },
        "Mission Reports": {
            "icon": "Crosshair",
            "subdivisions": {"Mission Report-01": []},
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

DEFAULT_USERS = {
    "TOA Terminal": {
        "password_hash": generate_password_hash("Paer-X"),
        "allowed_dbs": ["TOA"],
        "default_db": "TOA",
        "file_permissions": {"TOA": ["*"]},
        "builtin": True,
    },
    "BV Terminal": {
        "password_hash": generate_password_hash("Echo-Walker"),
        "allowed_dbs": ["BV"],
        "default_db": "BV",
        "file_permissions": {"BV": ["*"]},
        "builtin": True,
    },
}

DEFAULT_DATA = {
    "databases": INITIAL_DATABASES,
    "customNotes": {},
    "fileContents": INITIAL_FILE_DETAILS,
    "users": deepcopy(DEFAULT_USERS),
}


def collect_db_files(db: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for category in db.values():
        names.extend(category.get("files", []))
        for sub_files in category.get("subdivisions", {}).values():
            names.extend(sub_files)
    return sorted(set(names), key=str.casefold)


def ensure_user_shape(data: dict[str, Any]) -> None:
    data.setdefault("users", {})
    for username, defaults in DEFAULT_USERS.items():
        existing = data["users"].get(username, {})
        existing.setdefault("password_hash", defaults["password_hash"])
        existing["allowed_dbs"] = defaults["allowed_dbs"]
        existing["default_db"] = defaults["default_db"]
        existing["file_permissions"] = defaults["file_permissions"]
        existing["builtin"] = True
        data["users"][username] = existing

    for username, user in list(data["users"].items()):
        allowed = [db for db in user.get("allowed_dbs", []) if db in data["databases"]]
        if not allowed:
            allowed = ["TOA"]
        user["allowed_dbs"] = allowed
        if user.get("default_db") not in allowed:
            user["default_db"] = allowed[0]
        user.setdefault("file_permissions", {})
        user.setdefault("builtin", False)

        for db_name in list(user["file_permissions"].keys()):
            if db_name not in data["databases"]:
                user["file_permissions"].pop(db_name, None)

        for db_name in allowed:
            perms = user["file_permissions"].get(db_name)
            if perms is None:
                user["file_permissions"][db_name] = ["*"] if user.get("builtin") else []
            else:
                valid = set(collect_db_files(data["databases"][db_name]))
                if "*" in perms:
                    user["file_permissions"][db_name] = ["*"]
                else:
                    user["file_permissions"][db_name] = sorted({name for name in perms if name in valid}, key=str.casefold)


def load_data() -> dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        data = deepcopy(DEFAULT_DATA)
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (json.JSONDecodeError, OSError):
        loaded = deepcopy(DEFAULT_DATA)

    for k, v in DEFAULT_DATA.items():
        if k not in loaded:
            loaded[k] = deepcopy(v)

    for name, text in INITIAL_FILE_DETAILS.items():
        loaded["fileContents"].setdefault(name, text)

    ensure_user_shape(loaded)
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
        data["fileContents"][file_name] = f"[FILE: {file_name}]\n\nNo archived text currently exists for this file."


def get_real_username() -> str:
    return str(session.get("username", ""))


def get_view_username() -> str:
    if is_admin() and session.get("view_as"):
        return str(session.get("view_as"))
    return get_real_username()


def get_allowed_dbs(data: dict[str, Any], username: str) -> list[str]:
    if username == "ADMIN":
        return list(data["databases"].keys())
    user = data["users"].get(username, {})
    allowed = [db for db in user.get("allowed_dbs", []) if db in data["databases"]]
    return allowed or ["TOA"]


def get_active_db(data: dict[str, Any]) -> str:
    active = str(session.get("active_db", "TOA"))
    username = get_view_username()
    allowed = get_allowed_dbs(data, username)
    if active not in allowed:
        active = allowed[0]
        session["active_db"] = active
    return active


def user_can_access_file(data: dict[str, Any], username: str, db_name: str, file_name: str) -> bool:
    if username == "ADMIN":
        return True
    user = data["users"].get(username)
    if not user:
        return False
    if db_name not in user.get("allowed_dbs", []):
        return False
    perms = user.get("file_permissions", {}).get(db_name, [])
    return "*" in perms or file_name in perms


def filtered_database_for_user(data: dict[str, Any], db_name: str, username: str) -> dict[str, Any]:
    db = deepcopy(data["databases"].get(db_name, {}))
    if username == "ADMIN":
        return db

    for category_name in list(db.keys()):
        category = db[category_name]
        category["files"] = [f for f in category.get("files", []) if user_can_access_file(data, username, db_name, f)]
        new_subs = {}
        for sub_name, files in category.get("subdivisions", {}).items():
            visible = [f for f in files if user_can_access_file(data, username, db_name, f)]
            if visible:
                new_subs[sub_name] = visible
        category["subdivisions"] = new_subs
        if not category["files"] and not category["subdivisions"]:
            db.pop(category_name, None)
    return db


def build_user_list(data: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for username, user in sorted(data["users"].items(), key=lambda item: item[0].casefold()):
        result.append({
            "username": username,
            "builtin": bool(user.get("builtin", False)),
            "allowed_dbs": user.get("allowed_dbs", []),
            "default_db": user.get("default_db", "TOA"),
        })
    return result


def build_state(data: dict[str, Any]) -> dict[str, Any]:
    view_user = get_view_username()
    active_db = get_active_db(data) if logged_in() else "TOA"
    visible_db = filtered_database_for_user(data, active_db, view_user) if logged_in() else data["databases"].get("TOA", {})
    return {
        "authenticated": logged_in(),
        "is_admin": is_admin(),
        "username": get_real_username(),
        "view_as": session.get("view_as", "") if is_admin() else "",
        "viewing_as": view_user if logged_in() else "",
        "active_db": active_db,
        "allowed_dbs": get_allowed_dbs(data, view_user) if logged_in() else ["TOA"],
        "databases": {active_db: visible_db},
        "customNotes": data["customNotes"],
        "fileContents": data["fileContents"],
        "users": build_user_list(data) if is_admin() else [],
    }


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
      --hover:#1a2040;
      --glow:0 0 10px rgba(169,124,255,.35), 0 0 20px rgba(169,124,255,.16);
    }

    *{box-sizing:border-box;font-family:'Orbitron',sans-serif !important;font-weight:800 !important;color:var(--text)}
    body{margin:0;background:radial-gradient(circle at top, rgba(160,110,255,.12), transparent 35%),linear-gradient(180deg,#03040a 0%,#080b14 100%)}
    .wrap{max-width:1450px;margin:0 auto;padding:18px}
    .card{background:rgba(13,16,32,.94);border:1px solid var(--border-soft);border-radius:14px;box-shadow:0 0 0 1px rgba(166,121,255,.08),0 0 28px rgba(109,69,214,.20)}
    .login-wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
    .login-card{width:100%;max-width:460px;padding:24px}
    h1,h2,h3,p{margin:0;color:var(--text-bright);text-shadow:var(--glow)}
    .title{font-size:30px;letter-spacing:2px}
    .sub{color:var(--muted);margin-top:8px;font-size:13px;text-shadow:0 0 8px rgba(169,124,255,.2)}
    .field{margin-top:18px}.field.small{margin-top:10px}
    label{display:block;margin-bottom:8px;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:1.5px;text-shadow:0 0 8px rgba(169,124,255,.15)}
    input,textarea,select{width:100%;background:#090c18;color:var(--text-bright);border:1px solid var(--border-soft);border-radius:10px;padding:12px 14px;font-size:13px;outline:none;box-shadow:inset 0 0 10px rgba(140,90,255,.08)}
    input:focus,textarea:focus,select:focus{border-color:var(--border);box-shadow:0 0 0 1px rgba(166,121,255,.35),0 0 14px rgba(166,121,255,.15)}
    textarea{resize:vertical}
    button{background:#1a2040;color:var(--text-bright);border:1px solid var(--border);border-radius:10px;padding:10px 14px;cursor:pointer;transition:.15s ease;text-shadow:var(--glow);box-shadow:0 0 12px rgba(166,121,255,.08)}
    button:hover{background:#252f5f;box-shadow:0 0 14px rgba(166,121,255,.18);transform:translateY(-1px)}
    button.danger{border-color:rgba(255,104,135,.55);color:#ffd8e1;background:#2b1620;text-shadow:0 0 10px rgba(255,104,135,.2)}
    button.danger:hover{background:#3b1c28} button.ghost{background:transparent;border-color:var(--border-soft)} button.full{width:100%}
    .topbar{display:flex;gap:12px;justify-content:space-between;align-items:flex-start;padding-bottom:14px;border-bottom:1px solid var(--border-soft);margin-bottom:18px;flex-wrap:wrap}
    .status{display:grid;grid-template-columns:1fr 2fr;gap:8px 14px;font-size:13px;color:var(--muted)} .status strong{color:var(--text-bright);text-shadow:var(--glow)}
    .layout{display:grid;grid-template-columns:320px 1fr;gap:18px}
    .panel{padding:16px}.header-row{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
    .tree-section{border-top:1px solid rgba(154,124,255,.15);padding-top:10px;margin-top:10px}
    .category{border:1px solid rgba(154,124,255,.16);border-radius:12px;margin-bottom:12px;overflow:hidden;background:rgba(255,255,255,.01)}
    .cat-header,.sub-header,.file-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
    .cat-header{padding:12px 14px;background:rgba(154,124,255,.05)} .cat-header:hover,.sub-header:hover,.file-row:hover{background:var(--hover)}
    .cat-left,.sub-left,.file-left{display:flex;align-items:center;gap:10px;min-width:0;flex:1;cursor:pointer}
    .cat-actions,.sub-actions,.file-actions{display:flex;gap:6px;flex-shrink:0}.mini{padding:5px 8px;font-size:11px;border-radius:8px}
    .cat-body{display:none;padding:10px 12px 12px 12px}.cat-body.open{display:block}
    .subbox{border:1px solid rgba(154,124,255,.12);border-radius:10px;margin-top:8px;overflow:hidden}
    .sub-header{padding:9px 12px}.sub-body{display:none;padding:8px 10px 10px 18px;border-top:1px solid rgba(154,124,255,.12)}.sub-body.open{display:block}
    .file-row{padding:8px 10px;border-radius:8px;margin-top:4px;color:var(--text-bright)}
    .muted{color:var(--muted)} .badge{display:inline-block;border:1px solid rgba(138,255,193,.35);color:var(--success);padding:2px 8px;border-radius:999px;font-size:10px;text-shadow:0 0 8px rgba(138,255,193,.2)}
    .pill{display:inline-block;padding:3px 8px;border:1px solid rgba(166,121,255,.35);border-radius:999px;font-size:10px;color:var(--text-bright)}
    .dialog-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.66);display:none;align-items:center;justify-content:center;padding:20px;z-index:50}
    .dialog-backdrop.open{display:flex}.dialog{width:min(1050px,96vw);max-height:88vh;overflow:auto;padding:16px}
    .split{display:grid;grid-template-columns:1fr;gap:14px}.box{border:1px solid rgba(154,124,255,.15);border-radius:12px;padding:14px;background:rgba(255,255,255,.02)}
    .box-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
    pre{white-space:pre-wrap;word-break:break-word;color:var(--text-bright);margin:0;line-height:1.5;text-shadow:0 0 8px rgba(169,124,255,.12)}
    .row{display:flex;gap:10px;flex-wrap:wrap}.notice{margin-top:12px;font-size:13px;color:var(--muted);min-height:18px;text-shadow:0 0 8px rgba(169,124,255,.15)}
    .admin-box{margin-top:18px}.check-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;margin-top:10px}
    .check-item{display:flex;align-items:center;gap:8px;border:1px solid rgba(154,124,255,.12);border-radius:10px;padding:8px;background:rgba(255,255,255,.02)}
    .check-item input{width:auto;transform:scale(1.1)}
    @media (max-width:1100px){.layout{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div id="app"></div>
<script>
let state = {
  authenticated:false,is_admin:false,username:"",view_as:"",viewing_as:"",active_db:"TOA",allowed_dbs:["TOA"],
  databases:{},customNotes:{},fileContents:{},users:[],selectedFile:null,currentFileContent:"",currentEditNote:"",isEditingFile:false,
  categoryOpen:{},subdivisionOpen:{},editingUser:null,userEditor:null,permissionDb:"TOA"
};

function esc(s){return String(s ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")}
function attrEsc(s){return String(s ?? "").replaceAll("&","&amp;").replaceAll('"',"&quot;").replaceAll("<","&lt;").replaceAll(">","&gt;")}
function notify(msg,isError=false){const el=document.getElementById("notice");if(!el)return;el.textContent=msg;el.style.color=isError?"#ff9aae":"#aa89ec"}
async function api(path,method="GET",body=null){const opts={method,headers:{}};if(body!==null){opts.headers["Content-Type"]="application/json";opts.body=JSON.stringify(body)}const res=await fetch(path,opts);const data=await res.json();if(!res.ok||data.ok===false)throw new Error(data.error||"Request failed");return data}

async function loadState(){try{const data=await api("/api/state");state={...state,...data.state};render()}catch(err){document.getElementById("app").innerHTML='<div class="login-wrap"><div class="card login-card"><h1 class="title">ERROR</h1><p class="sub">'+esc(err.message)+'</p></div></div>'}}
async function refreshState(keepSelection=false){const selectedBefore=keepSelection?state.selectedFile:null;const fileContentBefore=keepSelection?state.currentFileContent:"";const noteBefore=keepSelection?state.currentEditNote:"";const editingBefore=keepSelection?state.isEditingFile:false;const editingUserBefore=state.editingUser;const userEditorBefore=state.userEditor;const permDbBefore=state.permissionDb;const data=await api("/api/state");state={...state,...data.state};state.editingUser=editingUserBefore;state.userEditor=userEditorBefore;state.permissionDb=permDbBefore||"TOA";if(keepSelection&&selectedBefore){state.selectedFile=selectedBefore;state.currentFileContent=fileContentBefore;state.currentEditNote=noteBefore;state.isEditingFile=editingBefore}render()}

function toggleCategory(name){state.categoryOpen[name]=!state.categoryOpen[name];render()}
function toggleSubdivision(cat,sub){const key=cat+"||"+sub;state.subdivisionOpen[key]=!state.subdivisionOpen[key];render()}

async function login(e){e.preventDefault();const username=document.getElementById("username").value;const password=document.getElementById("password").value;try{const data=await api("/api/login","POST",{username,password});state={...state,...data.state};render();notify(data.message||"Access granted")}catch(err){notify(err.message,true)}}
async function logout(){try{const data=await api("/api/logout","POST",{});state={...state,...data.state};render();notify(data.message||"Logged out")}catch(err){notify(err.message,true)}}
async function switchDb(targetDb=null){try{let nextDb=targetDb;if(!nextDb){const allowed=state.allowed_dbs||["TOA"];const idx=allowed.indexOf(state.active_db);nextDb=allowed[(idx+1)%allowed.length]}const data=await api("/api/switch_db","POST",{active_db:nextDb});state={...state,...data.state};state.selectedFile=null;state.currentFileContent="";state.currentEditNote="";state.isEditingFile=false;render()}catch(err){notify(err.message,true)}}

async function openFile(fileName){try{const data=await api("/api/file/"+encodeURIComponent(fileName));state.selectedFile=fileName;state.currentFileContent=data.file_content;state.currentEditNote=data.note;state.isEditingFile=false;render()}catch(err){notify(err.message,true)}}
function closeDialog(){state.selectedFile=null;state.currentFileContent="";state.currentEditNote="";state.isEditingFile=false;render()}
async function saveFileContent(){try{await api("/api/file/"+encodeURIComponent(state.selectedFile)+"/content","POST",{content:state.currentFileContent});await openFile(state.selectedFile);notify("Core file overwritten")}catch(err){notify(err.message,true)}}
async function saveAdminNote(){try{await api("/api/file/"+encodeURIComponent(state.selectedFile)+"/note","POST",{note:state.currentEditNote});await openFile(state.selectedFile);notify("Admin note saved")}catch(err){notify(err.message,true)}}

async function addEntry(){
  const type=prompt("What would you like to add?\n1. Category\n2. Subdivision\n3. File\nEnter 1, 2, or 3:");
  if(!type)return;
  if(type==="1"){const category=prompt("Enter new Category name:");if(!category)return;try{await api("/api/add/category","POST",{category});await refreshState()}catch(err){notify(err.message,true)}return}
  if(type==="2"){const categories=Object.keys(state.databases[state.active_db]||{});if(categories.length===0){alert("Please create a Category first.");return}const catList=categories.map((c,i)=>`${i+1}. ${c}`).join("\n");const catIndexStr=prompt(`Select a Category to add to (enter number):\n${catList}`);if(!catIndexStr)return;const catIndex=parseInt(catIndexStr,10)-1;const catName=categories[catIndex];if(!catName){alert("Invalid category selection.");return}const subdivision=prompt(`Enter new Subdivision name for ${catName}:`);if(!subdivision)return;try{await api("/api/add/subdivision","POST",{category:catName,subdivision});state.categoryOpen[catName]=true;await refreshState()}catch(err){notify(err.message,true)}return}
  if(type==="3"){const categories=Object.keys(state.databases[state.active_db]||{});if(categories.length===0){alert("Please create a Category first.");return}const catList=categories.map((c,i)=>`${i+1}. ${c}`).join("\n");const catIndexStr=prompt(`Select a Category to add to (enter number):\n${catList}`);if(!catIndexStr)return;const catIndex=parseInt(catIndexStr,10)-1;const catName=categories[catIndex];if(!catName){alert("Invalid category selection.");return}const subdivisions=Object.keys((state.databases[state.active_db][catName]||{}).subdivisions||{});let subName=null;if(subdivisions.length===0){const confirmNewSub=confirm(`No subdivisions found in ${catName}. Would you like to create one first? (Cancel adds directly to category)`);if(confirmNewSub){subName=prompt(`Enter new Subdivision name for ${catName}:`);if(!subName)return}}else{const subList=["0. None (Add directly to category)"];subdivisions.forEach((s,i)=>subList.push(`${i+1}. ${s}`));const subIndexStr=prompt(`Select a Subdivision in ${catName} (enter number):\n${subList.join("\n")}`);if(!subIndexStr)return;const subIndex=parseInt(subIndexStr,10);if(subIndex!==0){subName=subdivisions[subIndex-1];if(!subName){alert("Invalid subdivision selection.");return}}}const fileName=prompt(`Enter new File name for ${catName}${subName?" -> "+subName:""}:`);if(!fileName)return;try{await api("/api/add/file","POST",{category:catName,subdivision:subName,file_name:fileName});state.categoryOpen[catName]=true;if(subName)state.subdivisionOpen[catName+"||"+subName]=true;await refreshState()}catch(err){notify(err.message,true)}return}
  alert("Invalid selection. Please enter 1, 2, or 3.");
}

async function addSubdivisionOrFile(category){
  const type=prompt(`What wouldyou like to add to ${category}?\n1. Subdivision\n2. File\nEnter 1 or 2:`); if(!type)return;
  if(type==="1"){const subdivision=prompt(`Enter new Subdivision name for ${category}:`);if(!subdivision)return;try{await api("/api/add/subdivision","POST",{category,subdivision});state.categoryOpen[category]=true;await refreshState()}catch(err){notify(err.message,true)}return}
  if(type==="2"){const subdivisions=Object.keys((state.databases[state.active_db][category]||{}).subdivisions||{});let subName=null;if(subdivisions.length===0){const confirmNewSub=confirm(`No subdivisions found in ${category}. Would you like to create one first? (Cancel adds directly to category)`);if(confirmNewSub){subName=prompt(`Enter new Subdivision name for ${category}:`);if(!subName)return}}else{const subList=["0. None (Add directly to category)"];subdivisions.forEach((s,i)=>subList.push(`${i+1}. ${s}`));const subIndexStr=prompt(`Select a Subdivision in ${category} to add the file to (enter number):\n${subList.join("\n")}`);if(!subIndexStr)return;const subIndex=parseInt(subIndexStr,10);if(subIndex!==0){subName=subdivisions[subIndex-1];if(!subName){alert("Invalid subdivision selection.");return}}}const fileName=prompt(`Enter new File name for ${category}${subName?" -> "+subName:""}:`);if(!fileName)return;try{await api("/api/add/file","POST",{category,subdivision:subName,file_name:fileName});state.categoryOpen[category]=true;if(subName)state.subdivisionOpen[category+"||"+subName]=true;await refreshState()}catch(err){notify(err.message,true)}return}
  alert("Invalid selection. Please enter 1 or 2.");
}
async function addFile(category,subdivision){const fileName=prompt("Enter new File name:");if(!fileName)return;try{await api("/api/add/file","POST",{category,subdivision,file_name:fileName});state.categoryOpen[category]=true;if(subdivision)state.subdivisionOpen[category+"||"+subdivision]=true;await refreshState()}catch(err){notify(err.message,true)}}
async function removeCategory(category){if(!confirm(`Are you sure you want to delete category "${category}"?`))return;try{await api("/api/delete/category","POST",{category});if(state.selectedFile)closeDialog();delete state.categoryOpen[category];await refreshState()}catch(err){notify(err.message,true)}}
async function removeSubdivision(category,subdivision){if(!confirm(`Are you sure you want to delete subdivision "${subdivision}"?`))return;try{await api("/api/delete/subdivision","POST",{category,subdivision});delete state.subdivisionOpen[category+"||"+subdivision];await refreshState()}catch(err){notify(err.message,true)}}
async function removeFile(category,subdivision,fileName){if(!confirm(`Are you sure you want to delete file "${fileName}"?`))return;try{await api("/api/delete/file","POST",{category,subdivision,file_name:fileName});if(state.selectedFile===fileName)closeDialog();await refreshState()}catch(err){notify(err.message,true)}}

async function setViewAs(username){try{const data=await api("/api/admin/view_as","POST",{username});state={...state,...data.state};render();notify(`Viewing as ${username||'ADMIN'}`)}catch(err){notify(err.message,true)}}
async function loadUserEditor(username){try{const data=await api("/api/admin/user/"+encodeURIComponent(username));state.editingUser=username;state.userEditor=data.user;state.permissionDb=(data.user.allowed_dbs||["TOA"])[0]||"TOA";render()}catch(err){notify(err.message,true)}}
function startNewUser(){state.editingUser=null;state.userEditor={username:"",password:"",allowed_dbs:["TOA"],default_db:"TOA",file_permissions:{TOA:[]},builtin:false};state.permissionDb="TOA";render()}
function syncEditor(){if(!state.userEditor)return;const username=document.getElementById("adminUserName");const password=document.getElementById("adminUserPassword");const defaultDb=document.getElementById("adminDefaultDb");if(username)state.userEditor.username=username.value.trim();if(password)state.userEditor.password=password.value;if(defaultDb)state.userEditor.default_db=defaultDb.value;const allowed=Array.from(document.querySelectorAll("input[data-allow-db]:checked")).map(el=>el.value);state.userEditor.allowed_dbs=allowed.length?allowed:["TOA"];if(!state.userEditor.allowed_dbs.includes(state.permissionDb))state.permissionDb=state.userEditor.allowed_dbs[0];if(!state.userEditor.allowed_dbs.includes(state.userEditor.default_db))state.userEditor.default_db=state.userEditor.allowed_dbs[0];state.userEditor.file_permissions=state.userEditor.file_permissions||{};for(const db of ["TOA","BV"]){if(!state.userEditor.allowed_dbs.includes(db))delete state.userEditor.file_permissions[db];else if(!state.userEditor.file_permissions[db])state.userEditor.file_permissions[db]=[]}}
function getAllFilesForEditorDb(){const db=state.databases[state.active_db]||{};return []}
function getFilesForPermissionDb(){const dbName=state.permissionDb;const all=[];const source=window.fullDatabaseMap?.[dbName]||{};for(const [category,catData] of Object.entries(source)){for(const file of (catData.files||[]))all.push({category,subdivision:"",file_name:file});for(const [sub,files] of Object.entries(catData.subdivisions||{})){for(const file of files)all.push({category,subdivision:sub,file_name:file})}}return all}
function togglePermission(fileName){syncEditor();const db=state.permissionDb;const current=new Set(state.userEditor.file_permissions[db]||[]);if(current.has(fileName))current.delete(fileName);else current.add(fileName);state.userEditor.file_permissions[db]=Array.from(current);render()}
function toggleAllPermissions(){syncEditor();const db=state.permissionDb;const files=getFilesForPermissionDb().map(x=>x.file_name);const current=new Set(state.userEditor.file_permissions[db]||[]);const allSelected=files.length>0&&files.every(f=>current.has(f));state.userEditor.file_permissions[db]=allSelected?[]:files;render()}
async function saveUser(){syncEditor();try{const data=await api("/api/admin/user/save","POST",state.userEditor);await refreshState();await loadUserEditor(data.saved_username);notify(`Saved ${data.saved_username}`)}catch(err){notify(err.message,true)}}
async function deleteUser(){if(!state.editingUser)return;if(!confirm(`Delete user "${state.editingUser}"?`))return;try{await api("/api/admin/user/delete","POST",{username:state.editingUser});state.editingUser=null;state.userEditor=null;await refreshState();notify("User deleted")}catch(err){notify(err.message,true)}}

function renderLogin(){document.getElementById("app").innerHTML=`<div class="login-wrap"><div class="card login-card"><h1 class="title">RESTRICTED ACCESS</h1><p class="sub">TERMINAL AUTHORIZATION REQUIRED</p><form id="loginForm"><div class="field"><label>Operator ID</label><input id="username" type="text" placeholder="ENTER OPERATOR ID"></div><div class="field"><label>Passcode</label><input id="password" type="password" placeholder="ENTER PASSCODE"></div><div class="field"><button class="full" type="submit">INITIALIZE CONNECTION</button></div><div id="notice" class="notice"></div></form></div></div>`;document.getElementById("loginForm").addEventListener("submit",login)}

function renderAdminBox(){
  if(!state.is_admin)return "";
  const u=state.userEditor;
  const currentMeta=state.users.find(x=>x.username===state.editingUser);
  const builtin=!!currentMeta?.builtin;
  const source=window.fullDatabaseMap||{};
  const files=getFilesForPermissionDb();
  const selected=(u?.file_permissions?.[state.permissionDb])||[];
  return `<div class="card panel admin-box"><div class="header-row"><div><h2>USER CONTROL</h2><p class="sub">CUSTOM USERS, FILE ACCESS, AND VIEW SWITCHING.</p></div><div class="row"><button class="ghost" data-action="new-user">NEW USER</button></div></div>
    <div class="box" style="margin-bottom:14px;"><div class="box-head"><h3>VIEW AS</h3></div><select id="viewAsSelect"><option value="">ADMIN</option>${state.users.map(user=>`<option value="${attrEsc(user.username)}" ${state.view_as===user.username?"selected":""}>${esc(user.username)}</option>`).join("")}</select></div>
    <div class="box" style="margin-bottom:14px;"><div class="box-head"><h3>EXISTING USERS</h3></div><div class="row">${state.users.map(user=>`<button class="ghost mini" data-action="edit-user" data-username="${attrEsc(user.username)}">${esc(user.username)}</button>`).join("")}</div></div>
    <div class="box">${u?`<div class="box-head"><h3>${state.editingUser?`EDIT USER: ${esc(state.editingUser)}`:'CREATE USER'}</h3>${state.editingUser&&!builtin?`<button class="danger" data-action="delete-user">DELETE USER</button>`:""}</div>
      <div class="field"><label>Username</label><input id="adminUserName" type="text" value="${attrEsc(u.username||"")}" ${builtin?"disabled":""}></div>
      <div class="field"><label>${state.editingUser?"New Password (leave blank to keep current)":"Password"}</label><input id="adminUserPassword" type="password" value=""></div>
      <div class="field"><label>Allowed Databases</label><div class="check-list">${["TOA","BV"].map(db=>`<label class="check-item"><input type="checkbox" data-allow-db value="${db}" ${(u.allowed_dbs||[]).includes(db)?"checked":""}><span>${db}</span></label>`).join("")}</div></div>
      <div class="field"><label>Default Database</label><select id="adminDefaultDb">${(u.allowed_dbs||["TOA"]).map(db=>`<option value="${attrEsc(db)}" ${u.default_db===db?"selected":""}>${esc(db)}</option>`).join("")}</select></div>
      <div class="field"><label>File Permissions Database</label><div class="row"><select id="permissionDbSelect">${(u.allowed_dbs||["TOA"]).map(db=>`<option value="${attrEsc(db)}" ${state.permissionDb===db?"selected":""}>${esc(db)}</option>`).join("")}</select><button class="ghost" data-action="toggle-all-perms">TOGGLE ALL</button></div></div>
      <div class="check-list">${files.length?files.map(item=>`<label class="check-item"><input type="checkbox" data-action="toggle-perm" data-file="${attrEsc(item.file_name)}" ${selected.includes(item.file_name)?"checked":""}><span>${esc(item.file_name)} <span class="muted">(${esc(item.category)}${item.subdivision?` / ${esc(item.subdivision)}`:""})</span></span></label>`).join(""):`<div class="muted">No files in this database.</div>`}</div>
      <div class="field"><button data-action="save-user">SAVE USER</button></div>`:`<div class="muted">Pick a user to edit, or click NEW USER.</div>`}
    </div></div>`
}

function renderMain(){
  const db=state.databases[state.active_db]||{}; window.fullDatabaseMap=window.fullDatabaseMap||{}; window.fullDatabaseMap[state.active_db]=db; const isAdmin=state.is_admin;
  let categoriesHtml="";
  for(const [category,data] of Object.entries(db)){
    const catOpen=!!state.categoryOpen[category];
    const directFiles=(data.files||[]).map(file=>`<div class="file-row"><div class="file-left" data-action="open-file" data-file="${attrEsc(file)}"><span>📄</span><span>${esc(file)}</span>${state.customNotes[file]&&!isAdmin?'<span class="badge">NOTE</span>':''}</div>${isAdmin?`<div class="file-actions"><button class="mini danger" data-action="delete-file" data-category="${attrEsc(category)}" data-file="${attrEsc(file)}">DEL</button></div>`:""}</div>`).join("");
    const subdivisionsHtml=Object.entries(data.subdivisions||{}).map(([subdiv,files])=>{const key=category+"||"+subdiv;const subOpen=!!state.subdivisionOpen[key];const fileRows=(files||[]).length>0?files.map(file=>`<div class="file-row"><div class="file-left" data-action="open-file" data-file="${attrEsc(file)}"><span>📄</span><span>${esc(file)}</span>${state.customNotes[file]&&!isAdmin?'<span class="badge">NOTE</span>':''}</div>${isAdmin?`<div class="file-actions"><button class="mini danger" data-action="delete-file" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}" data-file="${attrEsc(file)}">DEL</button></div>`:""}</div>`).join(""):`<div class="muted" style="padding:8px 10px;">NO FILES PRESENT.</div>`; return `<div class="subbox"><div class="sub-header"><div class="sub-left" data-action="toggle-subdivision" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}"><span>📁</span><span>${esc(subdiv)}</span></div>${isAdmin?`<div class="sub-actions"><button class="mini ghost" data-action="add-file" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}">ADD FILE</button><button class="mini danger" data-action="delete-subdivision" data-category="${attrEsc(category)}" data-subdivision="${attrEsc(subdiv)}">DEL SUB</button></div>`:""}</div><div class="sub-body ${subOpen?"open":""}">${fileRows}</div></div>`}).join("");
    categoriesHtml += `<div class="category"><div class="cat-header"><div class="cat-left" data-action="toggle-category" data-category="${attrEsc(category)}"><span>🗂</span><span>${esc(category)}</span></div>${isAdmin?`<div class="cat-actions"><button class="mini ghost" data-action="add-subdivision-or-file" data-category="${attrEsc(category)}">ADD</button><button class="mini danger" data-action="delete-category" data-category="${attrEsc(category)}">DEL</button></div>`:""}</div><div class="cat-body ${catOpen?"open":""}">${directFiles}${subdivisionsHtml}</div></div>`;
  }

  const selected=state.selectedFile; const dialogOpen=!!selected; const noteVisible=isAdmin||!!(selected&&state.customNotes[selected]); const canSwitchDb=(state.allowed_dbs||[]).length>1;
  document.getElementById("app").innerHTML=`<div class="wrap"><div class="topbar"><div><h1 class="title">${esc(state.active_db)}_TERMINAL</h1><p class="sub">SECURE CONNECTION ESTABLISHED // ${isAdmin?"ADMIN OVERRIDE ACTIVE":"STANDARD OP LEVEL"}</p>${isAdmin&&state.view_as?`<p class="sub">VIEWING AS: ${esc(state.view_as)}</p>`:""}</div><div class="row">${canSwitchDb?`<button data-action="switch-db">SWITCH DATABASE</button>`:""}<button class="danger" data-action="logout">TERMINATE</button></div></div><div class="layout"><div class="card panel"><div class="header-row"><h2>SYSTEM STATUS</h2></div><div class="status"><div>LOGGED IN AS:</div><strong>${esc(state.username||"UNKNOWN")}</strong><div>VIEWING AS:</div><strong>${esc(state.viewing_as||state.username||"UNKNOWN")}</strong><div>ACCESS LEVEL:</div><strong>${esc(isAdmin?"OMEGA-PRIME":"OMEGA")}</strong><div>ENCRYPTION:</div><strong>256-BIT QUANTUM</strong><div>DATABASE SYNC:</div><strong>100%</strong><div>ACTIVE NODE:</div><strong>${esc(state.active_db)} ROOT</strong></div></div><div class="card panel"><div class="header-row"><div><h2>MAIN_DIRECTORY</h2><p class="sub">NAVIGATE THE ARCHIVAL RECORDS BELOW.</p></div>${isAdmin?`<button data-action="add-entry">ADD ENTRY</button>`:""}</div><div class="tree-section">${categoriesHtml||'<div class="muted">NO CATEGORIES AVAILABLE FOR THIS USER.</div>'}</div></div></div>${renderAdminBox()}<div id="notice" class="notice"></div></div><div class="dialog-backdrop ${dialogOpen?"open":""}" id="dialogBackdrop"><div class="card dialog"><div class="header-row"><h2>📄 ${esc(selected||"")}</h2><button class="ghost" data-action="close-dialog">CLOSE</button></div><div class="split"><div class="box"><div class="box-head"><h3>CORE FILE</h3>${isAdmin?`<div class="row">${state.isEditingFile?`<button data-action="save-file">SAVE</button><button class="danger" data-action="cancel-edit">CANCEL</button>`:`<button data-action="start-edit">EDIT</button>`}</div>`:""}</div>${isAdmin&&state.isEditingFile?`<textarea id="fileContentEditor" style="min-height:340px;">${esc(state.currentFileContent||"")}</textarea>`:`<pre>${esc(state.currentFileContent||"")}</pre>`}</div>${noteVisible?`<div class="box"><div class="box-head"><h3>ADMIN NOTES</h3>${isAdmin?`<button data-action="save-note">SAVE NOTE</button>`:""}</div>${isAdmin?`<textarea id="noteEditor" style="min-height:180px;">${esc(state.currentEditNote||"")}</textarea>`:`<pre>${esc((selected&&state.customNotes[selected])||"")}</pre>`}</div>`:""}</div></div></div>`;
  wireMainEvents();
  if(isAdmin&&state.isEditingFile){const ed=document.getElementById("fileContentEditor");if(ed)ed.addEventListener("input",e=>state.currentFileContent=e.target.value)}
  if(isAdmin&&dialogOpen){const noteEd=document.getElementById("noteEditor");if(noteEd)noteEd.addEventListener("input",e=>state.currentEditNote=e.target.value)}
  const viewAsSelect=document.getElementById("viewAsSelect"); if(viewAsSelect)viewAsSelect.addEventListener("change",e=>setViewAs(e.target.value));
  const permissionDbSelect=document.getElementById("permissionDbSelect"); if(permissionDbSelect)permissionDbSelect.addEventListener("change",e=>{syncEditor();state.permissionDb=e.target.value;render()});
  document.querySelectorAll("input[data-allow-db]").forEach(el=>el.addEventListener("change",()=>{syncEditor();render()}));
  const backdrop=document.getElementById("dialogBackdrop"); if(backdrop)backdrop.addEventListener("click",e=>{if(e.target===backdrop)closeDialog()});
}

function wireMainEvents(){document.querySelectorAll("[data-action]").forEach(el=>{el.addEventListener("click",async e=>{e.preventDefault();e.stopPropagation();const action=el.dataset.action;
  if(action==="logout")return logout(); if(action==="switch-db")return switchDb(); if(action==="add-entry")return addEntry(); if(action==="close-dialog")return closeDialog();
  if(action==="toggle-category")return toggleCategory(el.dataset.category); if(action==="toggle-subdivision")return toggleSubdivision(el.dataset.category,el.dataset.subdivision); if(action==="open-file")return openFile(el.dataset.file);
  if(action==="add-subdivision-or-file")return addSubdivisionOrFile(el.dataset.category); if(action==="delete-category")return removeCategory(el.dataset.category); if(action==="add-file")return addFile(el.dataset.category,el.dataset.subdivision); if(action==="delete-subdivision")return removeSubdivision(el.dataset.category,el.dataset.subdivision); if(action==="delete-file")return removeFile(el.dataset.category,el.dataset.subdivision||null,el.dataset.file);
  if(action==="start-edit"){state.isEditingFile=true;render();return} if(action==="cancel-edit"){if(state.selectedFile)return openFile(state.selectedFile);state.isEditingFile=false;render();return} if(action==="save-file")return saveFileContent(); if(action==="save-note")return saveAdminNote();
  if(action==="new-user")return startNewUser(); if(action==="edit-user")return loadUserEditor(el.dataset.username); if(action==="save-user")return saveUser(); if(action==="delete-user")return deleteUser(); if(action==="toggle-perm")return togglePermission(el.dataset.file); if(action==="toggle-all-perms")return toggleAllPermissions();
})})}

function render(){if(!state.authenticated)renderLogin();else renderMain()}
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
    return jsonify({"ok": True, "state": build_state(data)})


@app.post("/api/login")
def api_login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    if username == "ADMIN" and password == "TheWraith!13":
        session["authenticated"] = True
        session["is_admin"] = True
        session["username"] = username
        session["active_db"] = "TOA"
        session["view_as"] = ""
        msg = "ADMINISTRATIVE ACCESS GRANTED"
    elif username in ("TOA Terminal", "BV Terminal"):
        data = load_data()
        user = data["users"].get(username)
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            return jsonify({"ok": False, "error": "ACCESS DENIED: INVALID CREDENTIALS"}), 401
        session["authenticated"] = True
        session["is_admin"] = False
        session["username"] = username
        session["active_db"] = user.get("default_db", "TOA")
        session["view_as"] = ""
        msg = f"ACCESS GRANTED: {username}"
    else:
        data = load_data()
        user = data["users"].get(username)
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            return jsonify({"ok": False, "error": "ACCESS DENIED: INVALID CREDENTIALS"}), 401
        session["authenticated"] = True
        session["is_admin"] = False
        session["username"] = username
        session["active_db"] = user.get("default_db", "TOA")
        session["view_as"] = ""
        msg = f"ACCESS GRANTED: {username}"

    data = load_data()
    return jsonify({"ok": True, "message": msg, "state": build_state(data)})


@app.post("/api/logout")
def api_logout():
    session.clear()
    data = load_data()
    return jsonify({"ok": True, "message": "SYSTEM LOGOUT", "state": build_state(data)})


@app.post("/api/switch_db")
def api_switch_db():
    auth_err = require_login()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    active_db = str(body.get("active_db", "TOA"))
    data = load_data()
    if active_db not in data["databases"]:
        return jsonify({"ok": False, "error": "INVALID DATABASE"}), 400

    allowed = get_allowed_dbs(data, get_view_username())
    if active_db not in allowed:
        return jsonify({"ok": False, "error": "DATABASE ACCESS DENIED"}), 403

    session["active_db"] = active_db
    return jsonify({"ok": True, "state": build_state(data)})


@app.post("/api/admin/view_as")
def api_admin_view_as():
    auth_err = require_admin()
    if auth_err:
        return auth_err

    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    data = load_data()
    if username and username not in data["users"]:
        return jsonify({"ok": False, "error": "USER NOT FOUND"}), 404

    session["view_as"] = username
    allowed = get_allowed_dbs(data, username or "ADMIN")
    if session.get("active_db") not in allowed:
        session["active_db"] = allowed[0]

    return jsonify({"ok": True, "state": build_state(data)})


@app.get("/api/file/<path:file_name>")
def api_get_file(file_name: str):
    auth_err = require_login()
    if auth_err:
        return auth_err

    data = load_data()
    active_db = get_active_db(data)
    view_user = get_view_username()
    if not user_can_access_file(data, view_user, active_db, file_name):
        return jsonify({"ok": False, "error": "FILE ACCESS DENIED"}), 403

    ensure_file_content(data, file_name)
    save_data(data)
    return jsonify({
        "ok": True,
        "file_name": file_name,
        "file_content": data["fileContents"].get(file_name, f"[FILE: {file_name}]\n\nNo archived text currently exists for this file."),
        "note": data["customNotes"].get(file_name, ""),
    })


@app.post("/api/file/<path:file_name>/content")
def api_set_file_content(file_name: str):
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    data = load_data()
    data["fileContents"][file_name] = body.get("content", "")
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/file/<path:file_name>/note")
def api_set_file_note(file_name: str):
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    data = load_data()
    data["customNotes"][file_name] = body.get("note", "")
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/add/category")
def api_add_category():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    category = str(body.get("category", "")).strip()
    if not category:
        return jsonify({"ok": False, "error": "MISSING CATEGORY"}), 400
    data = load_data()
    active_db = get_active_db(data)
    data["databases"][active_db][category] = {"icon": "Folder", "subdivisions": {}, "files": []}
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/add/subdivision")
def api_add_subdivision():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    category = str(body.get("category", "")).strip()
    subdivision = str(body.get("subdivision", "")).strip()
    if not category or not subdivision:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR SUBDIVISION"}), 400
    data = load_data()
    active_db = get_active_db(data)
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
    category = str(body.get("category", "")).strip()
    subdivision = body.get("subdivision")
    file_name = str(body.get("file_name", "")).strip()
    if not category or not file_name:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR FILE NAME"}), 400
    data = load_data()
    active_db = get_active_db(data)
    db = data["databases"][active_db]
    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404
    ensure_file_content(data, file_name)
    if subdivision:
        db[category].setdefault("subdivisions", {})
        db[category]["subdivisions"].setdefault(subdivision, [])
        if file_name not in db[category]["subdivisions"][subdivision]:
            db[category]["subdivisions"][subdivision].append(file_name)
    else:
        db[category].setdefault("files", [])
        if file_name not in db[category]["files"]:
            db[category]["files"].append(file_name)
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/category")
def api_delete_category():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    category = str(body.get("category", "")).strip()
    if not category:
        return jsonify({"ok": False, "error": "MISSING CATEGORY"}), 400
    data = load_data()
    active_db = get_active_db(data)
    data["databases"][active_db].pop(category, None)
    ensure_user_shape(data)
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/subdivision")
def api_delete_subdivision():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    category = str(body.get("category", "")).strip()
    subdivision = str(body.get("subdivision", "")).strip()
    if not category or not subdivision:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR SUBDIVISION"}), 400
    data = load_data()
    active_db = get_active_db(data)
    db = data["databases"][active_db]
    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404
    db[category].setdefault("subdivisions", {})
    db[category]["subdivisions"].pop(subdivision, None)
    ensure_user_shape(data)
    save_data(data)
    return jsonify({"ok": True})


@app.post("/api/delete/file")
def api_delete_file():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    category = str(body.get("category", "")).strip()
    subdivision = body.get("subdivision")
    file_name = str(body.get("file_name", "")).strip()
    if not category or not file_name:
        return jsonify({"ok": False, "error": "MISSING CATEGORY OR FILE NAME"}), 400
    data = load_data()
    active_db = get_active_db(data)
    db = data["databases"][active_db]
    if category not in db:
        return jsonify({"ok": False, "error": "CATEGORY NOT FOUND"}), 404
    if subdivision:
        files = db[category].get("subdivisions", {}).get(subdivision, [])
        db[category]["subdivisions"][subdivision] = [f for f in files if f != file_name]
    else:
        db[category]["files"] = [f for f in db[category].get("files", []) if f != file_name]
    for user in data["users"].values():
        for db_name, perms in list(user.get("file_permissions", {}).items()):
            if "*" not in perms:
                user["file_permissions"][db_name] = [f for f in perms if f != file_name]
    save_data(data)
    return jsonify({"ok": True})


@app.get("/api/admin/user/<path:username>")
def api_admin_get_user(username: str):
    auth_err = require_admin()
    if auth_err:
        return auth_err
    data = load_data()
    user = data["users"].get(username)
    if not user:
        return jsonify({"ok": False, "error": "USER NOT FOUND"}), 404
    all_dbs = {db_name: collect_db_files(db) for db_name, db in data["databases"].items()}
    return jsonify({
        "ok": True,
        "user": {
            "username": username,
            "password": "",
            "allowed_dbs": user.get("allowed_dbs", []),
            "default_db": user.get("default_db", "TOA"),
            "file_permissions": user.get("file_permissions", {}),
            "builtin": bool(user.get("builtin", False)),
            "all_databases": all_dbs,
        },
    })


@app.post("/api/admin/user/save")
def api_admin_save_user():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    allowed_dbs = [db for db in body.get("allowed_dbs", []) if db in ("TOA", "BV")]
    default_db = str(body.get("default_db", "")).strip()
    file_permissions = body.get("file_permissions", {}) or {}
    if not username:
        return jsonify({"ok": False, "error": "USERNAME REQUIRED"}), 400
    if username.upper() == "ADMIN":
        return jsonify({"ok": False, "error": "ADMIN USERNAME IS RESERVED"}), 400
    if not allowed_dbs:
        return jsonify({"ok": False, "error": "SELECT AT LEAST ONE DATABASE"}), 400

    data = load_data()
    existing = data["users"].get(username)
    builtin = bool(existing and existing.get("builtin", False))
    if not existing and not password:
        return jsonify({"ok": False, "error": "PASSWORD REQUIRED FOR NEW USER"}), 400
    if default_db not in allowed_dbs:
        default_db = allowed_dbs[0]

    password_hash = existing.get("password_hash", "") if existing else ""
    if password:
        password_hash = generate_password_hash(password)

    normalized_permissions: dict[str, list[str]] = {}
    for db_name in allowed_dbs:
        valid = set(collect_db_files(data["databases"][db_name]))
        requested = file_permissions.get(db_name, []) or []
        normalized_permissions[db_name] = [f for f in requested if f in valid]

    data["users"][username] = {
        "password_hash": password_hash,
        "allowed_dbs": allowed_dbs,
        "default_db": default_db,
        "file_permissions": normalized_permissions if not builtin else DEFAULT_USERS[username]["file_permissions"],
        "builtin": builtin,
    }

    if builtin:
        data["users"][username]["allowed_dbs"] = DEFAULT_USERS[username]["allowed_dbs"]
        data["users"][username]["default_db"] = DEFAULT_USERS[username]["default_db"]

    save_data(data)
    return jsonify({"ok": True, "saved_username": username})


@app.post("/api/admin/user/delete")
def api_admin_delete_user():
    auth_err = require_admin()
    if auth_err:
        return auth_err
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    if not username:
        return jsonify({"ok": False, "error": "USERNAME REQUIRED"}), 400
    data = load_data()
    user = data["users"].get(username)
    if not user:
        return jsonify({"ok": False, "error": "USER NOT FOUND"}), 404
    if user.get("builtin"):
        return jsonify({"ok": False, "error": "BUILT-IN USERS CANNOT BE DELETED"}), 400
    data["users"].pop(username, None)
    if session.get("view_as") == username:
        session["view_as"] = ""
    save_data(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

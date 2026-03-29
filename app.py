from flask import Flask, request, jsonify, session, redirect
import os, json, secrets
from copy import deepcopy

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATA_FILE = "archive_data.json"

# ---------------- DEFAULT DATA ----------------

DEFAULT_DATA = {
    "databases": {
        "TOA": {},
        "BV": {},
        "INFO": {}
    },
    "users": {
        "ADMIN": {"password": "admin", "admin": True, "self_admin": True},
        "TOA": {"password": "toa", "admin": False},
        "BV": {"password": "bv", "admin": False}
    },
    "suggestions": []
}

# ---------------- LOAD / SAVE ----------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return deepcopy(DEFAULT_DATA)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- AUTH ----------------

def current_user():
    return session.get("user")

def require_login():
    if "user" not in session:
        return jsonify({"error": "login required"}), 403

def require_admin():
    data = load_data()
    user = session.get("user")
    if not user or not data["users"].get(user, {}).get("admin"):
        return jsonify({"error": "admin only"}), 403

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return """
    <h1>Archive Terminal</h1>
    <button onclick="location.href='/login'">Login</button>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return """
        <form method="POST">
            <input name="user" placeholder="user"><br>
            <input name="password" placeholder="password"><br>
            <button type="submit">Login</button>
        </form>
        """

    data = load_data()
    user = request.form["user"]
    pw = request.form["password"]

    if user in data["users"] and data["users"][user]["password"] == pw:
        session["user"] = user
        return redirect("/dashboard")

    return "Login failed"

@app.route("/dashboard")
def dashboard():
    if require_login():
        return require_login()

    user = session["user"]

    return f"""
    <h2>Welcome {user}</h2>

    <button onclick="location.href='/info'">INFO TERMINAL</button>
    <button onclick="location.href='/suggest'">Suggestion</button>
    <button onclick="location.href='/change_password'">Change Password</button>
    """

# ---------------- PASSWORD CHANGE ----------------

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if require_login():
        return require_login()

    if request.method == "GET":
        return """
        <form method="POST">
            <input name="new" placeholder="new password">
            <button type="submit">Change</button>
        </form>
        """

    data = load_data()
    user = session["user"]
    data["users"][user]["password"] = request.form["new"]
    save_data(data)

    return "Password updated"

# ---------------- INFO TERMINAL ----------------

@app.route("/info")
def info():
    if require_admin():
        return require_admin()

    data = load_data()
    return jsonify(data["databases"]["INFO"])

# ---------------- SUGGESTIONS ----------------

@app.route("/suggest", methods=["GET", "POST"])
def suggest():
    if require_login():
        return require_login()

    if request.method == "GET":
        return """
        <form method="POST">
            <input name="text" placeholder="suggestion">
            <button type="submit">Submit</button>
        </form>
        """

    data = load_data()
    data["suggestions"].append({
        "user": session["user"],
        "text": request.form["text"]
    })
    save_data(data)

    return "Suggestion submitted"

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

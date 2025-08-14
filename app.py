from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, requests, functools, time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "changeme")
app.config["GITHUB_USER"] = os.environ.get("GITHUB_USER", "ily6ix")
app.config["PROJECTS_CACHE_TTL"] = int(os.environ.get("PROJECTS_CACHE_TTL", "3600"))

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

with app.app_context():
    db.create_all()

def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def fetch_github_projects(user, max_count=3):
    
    try:
        resp = requests.get(
            f"https://api.github.com/users/{user}/repos",
            params={"sort": "pushed", "per_page": 20},
            timeout=10,
            headers={"Accept": "application/vnd.github+json"}
        )
        resp.raise_for_status()
        repos = resp.json()
    except Exception:
        return []
    clean = [r for r in repos if not r.get("fork") and not r.get("archived")]
    clean.sort(key=lambda r: r.get("pushed_at") or r.get("updated_at") or "", reverse=True)
    clean = clean[:max_count]
    projects = []
    for r in clean:
        name = r.get("name") or "repo"
        desc = r.get("description") or "No description provided."
        lang = r.get("language") or ""
        html_url = r.get("html_url")
        image = f"https://opengraph.githubassets.com/{int(time.time())}/{user}/{name}"
        projects.append({
            "title": name,
            "desc": desc,
            "tags": [lang] if lang else [],
            "image_url": image,
            "links": {"code": html_url, "live": ""},
        })
    return projects

_projects_cache = {"data": None, "at": 0}
def get_cached_projects():
    now = time.time()
    ttl = app.config["PROJECTS_CACHE_TTL"]
    if _projects_cache["data"] and now - _projects_cache["at"] < ttl:
        return _projects_cache["data"]
    data = fetch_github_projects(app.config["GITHUB_USER"], max_count=7)
    _projects_cache["data"] = data
    _projects_cache["at"] = now
    return data

@app.route("/")
def home():
    projects = get_cached_projects()
    return render_template("index.html", projects=projects)

@app.post("/contact")
def contact_submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    content = request.form.get("message", "").strip()
    if not name or not email or not content:
        flash("Please fill in all fields.", "danger")
        return redirect(url_for("home") + "#contact")
    msg = Message(name=name, email=email, message=content)
    db.session.add(msg)
    db.session.commit()
    flash("Thanks! Your message was sent successfully.", "success")
    return redirect(url_for("home") + "#contact")

@app.get("/admin/login")
def admin_login():
    return render_template("admin_login.html")

@app.post("/admin/login")
def admin_login_post():
    password = request.form.get("password", "")
    if password == "12345":
        session["admin_logged_in"] = True
        flash("Welcome, admin.", "success")
        next_url = request.args.get("next") or url_for("admin_messages")
        return redirect(next_url)
    flash("Invalid password.", "danger")
    return redirect(url_for("admin_login"))

@app.post("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("home"))

from flask import send_from_directory

@app.route('/download-cv')
def download_cv():
    return send_from_directory('static/files', 'cv-1.pdf', as_attachment=True)


@app.get("/admin/messages")
@login_required
def admin_messages():
    msgs = Message.query.order_by(Message.created_at.desc()).limit(100).all()
    return render_template("admin_messages.html", messages=msgs)

@app.post("/admin/refresh-projects")
@login_required
def refresh_projects():
    global _projects_cache
    _projects_cache = {"data": None, "at": 0}
    flash("Projects cache refreshed.", "success")
    return redirect(url_for("home") + "#projects")

#if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

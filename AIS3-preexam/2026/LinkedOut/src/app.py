import os
import sqlite3
from pathlib import Path, PurePosixPath

import requests
from flask import Flask, abort, g, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from lib import admin_models, recruiter_labs


APP_ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("LINKEDOUT_DB_PATH", "/tmp/linkedout.db"))
RENDERER_URL = os.environ.get("RENDERER_URL", "http://127.0.0.1:5001/render")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)


def get_db():
    if "db" not in g:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g.db = db
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )


def current_user():
    uid = session.get("uid")
    if uid is None:
        return None
    return get_db().execute(
        "SELECT id, email, password_hash FROM users WHERE id = ?",
        (uid,),
    ).fetchone()


def require_login():
    user = current_user()
    if user is None:
        return None, redirect("/login")
    return user, None


app.register_blueprint(recruiter_labs.create_blueprint(require_login))


@app.get("/")
def index():
    return render_template("index.html", title="LinkedOut")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        if "@" not in email or not password:
            error = "Invalid email or password."
        else:
            domain = email.rsplit("@", 1)[-1]
            db = get_db()
            if admin_models.public_signup_domain_blocked(domain, db):
                error = "Registration is not available for that email domain."
            else:
                try:
                    cur = db.execute(
                        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                        (email, generate_password_hash(password)),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "That email is already registered."
                else:
                    session["uid"] = cur.lastrowid
                    return redirect("/feed")

    return render_template("register.html", title="Register", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."
        else:
            session["uid"] = user["id"]
            return redirect("/feed")

    return render_template("login.html", title="Login", error=error)


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.get("/feed")
def feed():
    user, response = require_login()
    if response is not None:
        return response
    return render_template("feed.html", title="Your feed", user=user)


@app.route("/compose", methods=["GET", "POST"])
def compose():
    user, response = require_login()
    if response is not None:
        return response

    rendered = None
    if request.method == "POST":
        body = request.form.get("body", "")
        payload = {"body": body, "user": {"id": user["id"], "email": user["email"]}}
        try:
            resp = requests.post(RENDERER_URL, json=payload, timeout=3)
            rendered = resp.json().get("rendered", "")
        except Exception as exc:
            rendered = f"renderer unavailable: {exc.__class__.__name__}"

    return render_template(
        "compose.html",
        title="Compose",
        user=user,
        rendered=rendered,
    )


@app.get("/media")
def media():
    _user, response = require_login()
    if response is not None:
        return response

    requested = request.args.get("file", "")
    path = PurePosixPath(requested)
    if not requested or path.is_absolute() or ".." in path.parts:
        abort(404)

    if "lib" in requested.lower():
        abort(404)

    target = (APP_ROOT / Path(*path.parts)).resolve()
    try:
        target.relative_to(APP_ROOT)
    except ValueError:
        abort(404)

    if not target.is_file():
        abort(404)

    return target.read_bytes(), 200, {"Content-Type": content_type_for(target)}


def content_type_for(path):
    if path.suffix == ".png":
        return "image/png"
    if path.suffix == ".txt":
        return "text/plain; charset=utf-8"
    return "text/plain; charset=utf-8"


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

from flask import Flask, request, render_template, redirect, url_for, session
import os
import uuid
import re
import socket
from markdown_parser import parse_markdown
from db import Database

app = Flask(__name__)
app.secret_key = os.urandom(32)

BOT_PORT = int(os.getenv("BOT_PORT", 8080))
BOT_HOST = os.getenv("BOT_HOST", "markdown-bot")
SITE_URL = os.getenv("SITE_URL", "http://markdown/")

db = Database()


@app.before_request
def before_request():
    if "id" not in session:
        session["id"] = uuid.uuid4().hex


@app.route("/", methods=["GET", "POST"])
def index():
    """Index page"""
    if request.method == "POST":
        content = request.form.get("note")
        if content:
            db.create_note(session["id"], content)
        return redirect(url_for("index"))

    notes = db.get_user_notes(session["id"])
    return render_template("index.html", notes=notes)


@app.route("/note/<note_id>")
def view_note(note_id):
    """View a note with markdown parser"""
    note = db.get_note_by_id(note_id)

    if not note:
        return "Note not found", 404

    html = parse_markdown(note["content"])
    return render_template("note.html", note=html)


@app.route("/report", methods=["GET", "POST"])
def report():
    """Just a report page for XSS chall"""
    response = None
    if request.method == "POST":
        url = request.form["url"]
        pattern = "^" + SITE_URL
        print(f"{pattern=}", flush=True)
        if not url or not re.match(pattern, url):
            return "Invalid URL", 400

        print(f"[+] Sending {url} to bot", flush=True)

        try:
            client = socket.create_connection((BOT_HOST, BOT_PORT))
            client.sendall(url.encode())

            response = []
            while True:
                data = client.recv(1024)
                if not data:
                    break
                response.append(data.decode())
            client.close()
            return "".join(response)
        except Exception as e:
            print(e, flush=True)
            return "Something is wrong...", 500
    return render_template("report.html", response=response)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)

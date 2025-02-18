from flask import Flask, request, render_template, redirect, url_for
import uuid
import os
import re
import socket

app = Flask(__name__)
app.secret_key = "your_secret_key"

BOT_PORT = int(os.getenv("BOT_PORT", 8080))
BOT_HOST = os.getenv("BOT_HOST", "localhost")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        note = request.form.get("note")
        note_id = uuid.uuid4().hex
        with open(f"notes/{note_id}.txt", "w") as f:
            f.write(note)
        return redirect(url_for("view_note", note_id=note_id))

    return render_template("index.html")


@app.route("/note/<note_id>")
def view_note(note_id):
    if not os.path.exists(f"notes/{note_id}.txt"):
        return "Note not found", 404

    with open(f"notes/{note_id}.txt", "r") as f:
        note = f.read()
    return render_template("note.html", note=note)


@app.route("/report", methods=["GET", "POST"])
def report():
    response = None
    if request.method == "POST":
        url = request.form["url"]
        pattern = "^http://xss5/"
        print(f"{pattern=}")
        if not url or not re.match(pattern, url):
            return "Invalid URL", 400

        print(f"[+] Sending {url} to bot")

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
            print(e)
            return "Something is wrong...", 500
    return render_template("report.html", response=response)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

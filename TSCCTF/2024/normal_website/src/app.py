from flask import Flask, render_template, Response
from werkzeug.debug import DebuggedApplication
from base64 import b64decode
import os

DebuggedApplication._fail_pin_auth = lambda self: print("No need to bruteforce!", flush=True)

app = Flask(__name__)

@app.route("/img/<path>")
def get_img(path):
    path = b64decode(path).decode()
    image_path = os.path.join('static/', path)
    try:
        with open(image_path, 'rb') as file:
            return Response(file.read(), mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

@app.route("/")
def index():
    return render_template("index.html")
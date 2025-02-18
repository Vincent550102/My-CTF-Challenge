from flask import Flask, request, jsonify, render_template, send_file
from pymongo import MongoClient
from base64 import b64encode
from config import mongo_username, mongo_password, flag
import os

app = Flask(__name__)
client = MongoClient(
    f"mongodb://{mongo_username}:{mongo_password}@mongo:27017", connect=False
)
db = client["nosqlinjectionblind"]


@app.route("/login", methods=["POST"])
def login():
    users = db.users
    username = request.json.get("username")
    password = request.json.get("password")
    print(password, flush=True)

    user = users.find_one({"username": username, "password": password})

    if user:
        return jsonify(
            {
                "message": "Login successful",
            }
        )
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/")
def index():
    if request.args.get("debug"):
        return send_file(__name__ + ".py")
    return render_template("index.html")


@app.before_first_request
def initialize_database():
    users = db.users

    # Insert default users
    guest_user = {"username": "guest", "password": "guest"}
    users.update_one({"username": "guest"}, {"$set": guest_user}, upsert=True)

    # Insert secret user
    secret_user = {"username": "admin", "password": flag}
    users.update_one({"username": "admin"}, {"$set": secret_user}, upsert=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from config import mongo_username, mongo_password
import datetime
import hashlib
import uuid
import os
from idlelib import history

app = Flask(__name__)
app.secret_key = os.urandom(32)

client = MongoClient(
    f"mongodb://{mongo_username}:{mongo_password}@mongo:27017", connect=False
)
db = client["sqli_payloads"]
collection = db["payloads"]
users_collection = db["users"]
history_collection = db["history"]


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.json.get("username")
        password = request.json.get("password")

        if users_collection.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        users_collection.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "created_at": datetime.datetime.utcnow(),
            }
        )

        return jsonify({"message": "Registration successful"})
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.json.get("username")
        password = request.json.get("password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = users_collection.find_one(
            {"username": username, "password": hashed_password}
        )

        if user:
            session["username"] = username
            return jsonify({"message": "Login successful"})
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    types = collection.distinct("type")
    history = []
    for item in history_collection.find({"username": session["username"]}).sort(
        "created_at", -1
    ):
        item_dict = {
            "_id": str(item["_id"]),
            "username": item["username"],
            "payload_type": item["payload_type"],
            "field": item["field"],
            "custom_value": item.get("custom_value", ""),
            "generated_payload": item["generated_payload"],
            "created_at": item["created_at"],
            "favorite": item.get("favorite", False),
        }
        history.append(item_dict)

    return render_template(
        "index.html", username=session["username"], payload_types=types, history=history
    )


@app.route("/generate", methods=["POST"])
def generate_payload():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    field = data.get("field")
    payload_type = data.get("type")
    custom_value = data.get("value", "")

    payload_template = collection.find_one({"type": payload_type})
    if not payload_template:
        return jsonify({"error": "Payload type not found"}), 404

    payload = payload_template["template"]
    payload = payload.replace("{column}", field)
    if custom_value:
        payload = payload.replace("{value}", custom_value)

    history_id = str(uuid.uuid4())

    history_collection.insert_one(
        {
            "_id": history_id,
            "username": session["username"],
            "payload_type": payload_type,
            "field": field,
            "custom_value": custom_value,
            "generated_payload": payload,
            "created_at": datetime.datetime.utcnow(),
            "favorite": False,
        }
    )

    return jsonify({"payload": payload})


@app.route("/favorite", methods=["POST"])
def toggle_favorite():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    history_id = data.get("history_id")

    if not history_id:
        return jsonify({"error": "History ID required"}), 400

    history_item = history_collection.find_one(history_id)

    if not history_item:
        return jsonify({"error": "History not found"}), 404

    current_status = history_item.get("favorite", False)
    history_collection.update_one(
        {"_id": history_item.get("_id")}, {"$set": {"favorite": not current_status}}
    )

    return jsonify({"message": "Favorite status updated successfully"})


@app.before_first_request
def initialize_database():
    if collection.count_documents({}) == 0:
        default_payloads = [
            {
                "type": "union",
                "name": "Basic UNION Select",
                "template": "' UNION SELECT {value},NULL,NULL-- -",
                "description": "Basic UNION based injection",
            },
            {
                "type": "error",
                "name": "Error Based",
                "template": "' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT {column}),0x7e))-- -",
                "description": "Error based SQL injection using EXTRACTVALUE",
            },
            {
                "type": "blind",
                "name": "Blind Boolean",
                "template": "' AND SUBSTRING((SELECT {column} FROM users WHERE id=1),1,1)='{value}'-- -",
                "description": "Blind boolean based injection",
            },
            {
                "type": "time",
                "name": "Time Based",
                "template": "' AND IF({column}='{value}',SLEEP(5),0)-- -",
                "description": "Time based SQL injection",
            },
            {
                "type": "auth_bypass",
                "name": "Authentication Bypass",
                "template": "' OR '1'='1",
                "description": "Simple authentication bypass",
            },
            {
                "type": "stack",
                "name": "Stack Queries",
                "template": "'; {value}; SELECT * FROM users WHERE '1'='1",
                "description": "Stacked SQL injection queries",
            },
            {
                "type": "union_all",
                "name": "UNION ALL Select",
                "template": "' UNION ALL SELECT {value},NULL,NULL-- -",
                "description": "UNION ALL based injection",
            },
            {
                "type": "like",
                "name": "LIKE Operator",
                "template": "' OR {column} LIKE '{value}%'-- -",
                "description": "LIKE operator based injection",
            },
            {
                "type": "convert",
                "name": "Type Conversion",
                "template": "' AND CONVERT(int, {column})={value}-- -",
                "description": "Type conversion based injection",
            },
            {
                "type": "case",
                "name": "CASE Statement",
                "template": "' AND CASE WHEN ({column}='{value}') THEN 1 ELSE 0 END=1-- -",
                "description": "CASE statement based injection",
            },
        ]
        collection.insert_many(default_payloads)
    admin_user = users_collection.find_one({"username": "admin"})
    if not admin_user:
        hashed_password = hashlib.sha256(os.urandom(30)).hexdigest()
        users_collection.insert_one(
            {
                "username": "admin",
                "password": hashed_password,
                "created_at": datetime.datetime.utcnow(),
            }
        )

    admin_flag_history = history_collection.find_one(
        {"username": "admin", "payload_type": "flag"}
    )

    if not admin_flag_history:
        from config import flag

        history_collection.insert_one(
            {
                "_id": str(uuid.uuid4()),
                "username": "admin",
                "payload_type": "flag",
                "field": "secret",
                "custom_value": "flag",
                "generated_payload": flag,
                "created_at": datetime.datetime.utcnow(),
                "favorite": False,
            }
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

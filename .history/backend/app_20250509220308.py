from flask import Flask, Response, jsonify, render_template, request, redirect, url_for, flash, session
from db.mongo import db
import json
import datetime
from bson.objectid import ObjectId

app = Flask(__name__, template_folder="../frontend/templates")
app.secret_key = "your_secret_key_here"

customers = db.customers

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    print("Received login request for user:", username)
    print("Received password:", password)

    # Verify credentials in MongoDB admin collection
    user = db.admin.find_one({"username": username, "password": password})
    print("User found:", user)

    if user:
        # Convert ObjectId to string to make it JSON serializable
        user_id = str(user.get("_id"))

        # Extract relevant user data
        user_data = {
            "user_id": user_id,
            "username": user.get("username"),
            "name": user.get("name"),
        }

        # Store username in session
        session["username"] = user.get("username")

        # Authentication successful
        response = app.response_class(
            response=json.dumps(
                {
                    "status": "success",
                    "message": "Login successful",
                    "user_data": user_data,
                }
            ),
            status=200,
            mimetype="application/json",
        )
        return response
    else:
        # Authentication failed
        response = app.response_class(
            response=json.dumps(
                {"status": "error", "message": "Invalid credentials"}
            ),
            status=401,
            mimetype="application/json",
        )
        return response

@app.route("/dashboard")
def dashboard():
    if "username" in session:
        user_count = db.admin.count_documents({})
        return render_template(
            "dashboard.html", username=session["username"], user_count=user_count
        )
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/users")
def list_users():
    if "username" in session:
        users = list(db.admin.find())
        return render_template("users.html", users=users)
    return redirect(url_for("login"))

@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        if db.admin.find_one({"username": username}):
            flash("Username already exists.")
        else:
            db.admin.insert_one(
                {
                    "name": name,
                    "username": username,
                    "password": password,
                }
            )
            flash("User added successfully.")
        return redirect(url_for("list_users"))
    return render_template("add_user.html")

@app.route("/update-user/<username>", methods=["POST"])
def update_user(username):
    if "username" not in session:
        return redirect(url_for("login"))
    name = request.form["name"]
    password = request.form["password"]

    updates = {}
    if name:
        updates["name"] = name
    if password:
        updates["password"] = password

    if updates:
        db.admin.update_one(
            {"username": username},
            {"$set": updates}
        )
        flash(f"Updated user {username}.")
    else:
        flash("No changes provided.")
    return redirect(url_for("list_users"))

def parse_customer_id(cid_str):
    return int(cid_str) if cid_str.isdigit() else cid_str

# ─── CUSTOMER CRUD ────────────────────────────────────────────────────────────
@app.route("/api/customers", methods=["POST"])
def create_customer():
    data = request.get_json() or {}
    # auto-generate an integer ID
    if "customer_id" not in data:
        last_customer = customers.find_one(sort=[("customer_id", -1)])
        data["customer_id"] = (last_customer["customer_id"] + 1) if last_customer else 1

    cust = {
        "customer_id": data["customer_id"],
        "name":        data["name"],
        "email":       data["email"],
        "phone":       data["phone"],
        "type":        data.get("type", "Regular"),
        "datetime": datetime.datetime.now(datetime.timezone.utc)  # Thêm timezone
    }
    result = customers.insert_one(cust)
    cust["_id"]      = str(result.inserted_id)
    cust["datetime"] = cust["datetime"].isoformat()

    return jsonify(cust), 201

@app.route("/api/customers", methods=["GET"])
def get_customers():
    docs = customers.find({}, {"_id":0}).sort("datetime", -1)
    out  = []
    for d in docs:
        # if datetime is a datetime object, convert to string
        if hasattr(d.get("datetime"), "isoformat"):
            d["datetime"] = d["datetime"].isoformat()
        out.append(d)
    return jsonify(out), 200

@app.route("/api/customers/<cust_id>", methods=["GET"])
def get_customer(cust_id):
    key = parse_customer_id(cust_id)
    doc = customers.find_one({"customer_id": key}, {"_id":0})
    if not doc:
        return jsonify(error="Not found"), 404
    if hasattr(doc.get("datetime"), "isoformat"):
        doc["datetime"] = doc["datetime"].isoformat()
    return jsonify(doc), 200

@app.route("/api/customers/<cust_id>", methods=["PUT"])
def update_customer(cust_id):
    key = parse_customer_id(cust_id)
    data = request.get_json() or {}
    result = customers.update_one({"customer_id": key}, {"$set": data})
    if result.matched_count == 0:
        return jsonify(error="Not found"), 404
    return jsonify(modified_count=result.modified_count), 200

@app.route("/api/customers/<cust_id>", methods=["DELETE"])
def delete_customer(cust_id):
    key = parse_customer_id(cust_id)
    result = customers.delete_one({"customer_id": key})
    if result.deleted_count == 0:
        return jsonify(error="Not found"), 404
    return jsonify(deleted_count=result.deleted_count), 200

# ─── CUSTOMER Interaction ────────────────────────────────────────────────────────────
@app.route("/api/interactions", methods=["GET"])
def get_all_interactions():
    interactions = db.interactions.find()
    result = []
    for doc in interactions:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        # Optional: Format datetime if exists
        if "datetime" in doc and hasattr(doc["datetime"], "isoformat"):
            doc["datetime"] = doc["datetime"].isoformat()
        result.append(doc)
    return jsonify(result), 200

@app.route("/api/interactions", methods=["POST"])
def add_interaction():
    data = request.json or {}
    data["timestamp"] = datetime.datetime.utcnow()
    db.interactions.insert_one(data)
    return jsonify({"status": "success", "message": "Interaction saved"}), 201

if __name__ == "__main__":
    app.run(debug=True)
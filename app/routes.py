from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from .db import collection
from .utils import verify_signature

bp = Blueprint("main", __name__)


# ---------------------------
# UI Route
# ---------------------------
@bp.route("/")
def index():
    return render_template("index.html")


# ---------------------------
# Webhook Endpoint
# ---------------------------
@bp.route("/webhook", methods=["POST"])
def webhook():

    payload = request.data

    # If no secret set, skip verification (for testing)
    try:
        if not verify_signature(payload):
            return jsonify({"error": "Invalid signature"}), 403
    except Exception:
        pass  # Allows local testing without secret

    data = request.json
    event = request.headers.get("X-GitHub-Event")

    try:
        if event == "push":
            document = {
                "request_id": data.get("head_commit", {}).get("id"),
                "author": data.get("pusher", {}).get("name"),
                "action": "PUSH",
                "from_branch": None,
                "to_branch": data.get("ref", "").split("/")[-1],
                "timestamp": datetime.utcnow()
            }
            collection.insert_one(document)

        elif event == "pull_request":

            pr = data.get("pull_request", {})

            # Pull Request Opened
            if data.get("action") == "opened":
                document = {
                    "request_id": str(pr.get("id")),
                    "author": pr.get("user", {}).get("login"),
                    "action": "PULL_REQUEST",
                    "from_branch": pr.get("head", {}).get("ref"),
                    "to_branch": pr.get("base", {}).get("ref"),
                    "timestamp": datetime.utcnow()
                }
                collection.insert_one(document)

            # Merge Event
            if pr.get("merged") is True:
                document = {
                    "request_id": str(pr.get("id")),
                    "author": pr.get("user", {}).get("login"),
                    "action": "MERGE",
                    "from_branch": pr.get("head", {}).get("ref"),
                    "to_branch": pr.get("base", {}).get("ref"),
                    "timestamp": datetime.utcnow()
                }
                collection.insert_one(document)

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success"}), 200


# ---------------------------
# API for UI Polling
# ---------------------------
@bp.route("/events", methods=["GET"])
def get_events():
    return jsonify({"message": "events route working"}), 200

    try:
        events = []

        # Safe query (in case timestamp missing in old docs)
        cursor = collection.find().limit(20)

        for doc in cursor:
            events.append({
                "id": str(doc.get("_id")),
                "request_id": doc.get("request_id"),
                "author": doc.get("author"),
                "action": doc.get("action"),
                "from_branch": doc.get("from_branch"),
                "to_branch": doc.get("to_branch"),
                "timestamp": doc.get("timestamp").strftime("%d %B %Y - %I:%M %p UTC")
                if doc.get("timestamp") else None
            })

        # Sort safely in Python (avoids MongoDB sort crash)
        events = sorted(
            events,
            key=lambda x: x["timestamp"] if x["timestamp"] else "",
            reverse=True
        )

        return jsonify(events), 200

    except Exception as e:
        print("EVENT FETCH ERROR:", e)
        return jsonify({"error": str(e)}), 500
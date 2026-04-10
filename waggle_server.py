"""
WaggleDance - Communication server for Claude Code instances.

Named after the waggle dance of honeybees - the figure-eight dance
that bees use to communicate the direction and distance of resources
to their hive-mates. This server lets two Claude Code instances
(Laptop and Desktop) coordinate their work on KillerBee and GiantHoneyBee.

Run this on one machine. Both Claude Code instances talk to it via curl.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Messages stored in memory and saved to disk
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), "messages.json")
messages = []


def load_messages():
    global messages
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)


def save_messages():
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


@app.route("/send", methods=["POST"])
def send_message():
    """Send a message. POST JSON: {"from": "laptop", "message": "hello"}"""
    data = request.get_json()
    if not data or "from" not in data or "message" not in data:
        return jsonify({"error": "Need 'from' and 'message' fields"}), 400

    msg = {
        "id": len(messages) + 1,
        "from": data["from"],
        "type": data.get("type", "REPLY"),
        "message": data["message"],
        "timestamp": datetime.now().isoformat(),
    }
    messages.append(msg)
    save_messages()
    return jsonify({"ok": True, "id": msg["id"]})


@app.route("/read", methods=["GET"])
def read_messages():
    """Read messages. Optional ?since=ID to get only new messages."""
    since = request.args.get("since", 0, type=int)
    filtered = [m for m in messages if m["id"] > since]
    return jsonify({"messages": filtered, "total": len(messages)})


@app.route("/latest", methods=["GET"])
def latest():
    """Get the last N messages. Optional ?n=10 (default 10)."""
    n = request.args.get("n", 10, type=int)
    return jsonify({"messages": messages[-n:]})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "dancing", "messages_count": len(messages)})


if __name__ == "__main__":
    load_messages()
    print("WaggleDance server starting on port 8765...")
    print("Endpoints:")
    print("  POST /send        - Send a message: {\"from\": \"laptop\", \"message\": \"text\"}")
    print("  GET  /read        - Read all messages (or ?since=ID for new only)")
    print("  GET  /latest      - Last 10 messages (or ?n=N)")
    print("  GET  /health      - Server status")
    app.run(host="0.0.0.0", port=8765)

import uuid
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from audit import init_db, add_log_entry, get_logs, add_appeal
from confidence import combine_scores
from detector import llm_ai_score, heuristic_ai_score
from labels import get_attribution, get_transparency_label

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

init_db()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running",
        "endpoints": ["/submit", "/appeal", "/log", "/analytics"]
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json()

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({"error": "text and creator_id are required"}), 400

    text = data["text"]
    creator_id = data["creator_id"]
    content_id = str(uuid.uuid4())

    llm_score = llm_ai_score(text)
    heuristic_score = heuristic_ai_score(text)
    confidence = combine_scores(llm_score, heuristic_score)

    attribution = get_attribution(confidence)
    label = get_transparency_label(attribution)

    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "signals": {
            "llm_score": llm_score,
            "heuristic_score": heuristic_score
        },
        "status": "classified"
    }

    add_log_entry({
        "event_type": "classification",
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "heuristic_score": heuristic_score,
        "label": label,
        "status": "classified",
        "appeal_reasoning": None
    })

    return jsonify(response)


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    if not data or "content_id" not in data or "creator_reasoning" not in data:
        return jsonify({"error": "content_id and creator_reasoning are required"}), 400

    content_id = data["content_id"]
    creator_reasoning = data["creator_reasoning"]

    add_appeal(content_id, creator_reasoning)

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received and content marked for review."
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({
        "entries": get_logs()
    })


@app.route("/analytics", methods=["GET"])
def analytics():
    logs = get_logs(limit=100)

    classification_logs = [entry for entry in logs if entry["event_type"] == "classification"]
    appeal_logs = [entry for entry in logs if entry["event_type"] == "appeal"]

    total = len(classification_logs)

    likely_ai = sum(1 for entry in classification_logs if entry["attribution"] == "likely_ai")
    likely_human = sum(1 for entry in classification_logs if entry["attribution"] == "likely_human")
    uncertain = sum(1 for entry in classification_logs if entry["attribution"] == "uncertain")

    appeal_rate = 0
    if total > 0:
        appeal_rate = round(len(appeal_logs) / total, 2)

    return jsonify({
        "total_submissions": total,
        "likely_ai": likely_ai,
        "likely_human": likely_human,
        "uncertain": uncertain,
        "total_appeals": len(appeal_logs),
        "appeal_rate": appeal_rate
    })


if __name__ == "__main__":
    app.run(debug=True)
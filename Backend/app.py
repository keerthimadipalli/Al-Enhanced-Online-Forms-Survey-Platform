"""
FormFlow Backend – app.py
Flask REST API with ML prediction and GenAI integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime, os, joblib, json
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# ─── Database ─────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["formflow"]
users_col = db["users"]
forms_col = db["forms"]
responses_col = db["responses"]

# ─── GenAI ────────────────────────────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# ─── ML Model ─────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ML/model.pkl")
ml_model = None
try:
    ml_model = joblib.load(MODEL_PATH)
    print("[INFO] ML model loaded.")
except Exception as e:
    print(f"[WARN] ML model not loaded: {e}")


# ─── Helper ───────────────────────────────────────────────────────────────────
def serialize(doc):
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id", ""))
    return doc


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields required."})
    if users_col.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered."})

    users_col.insert_one({"name": name, "email": email, "password": password,
                           "created_at": datetime.datetime.utcnow()})
    return jsonify({"success": True})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = users_col.find_one({"email": email, "password": password})
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials."})
    return jsonify({"success": True, "user": {"name": user["name"], "email": user["email"]}})


# ══════════════════════════════════════════════════════════════════════════════
# FORMS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/forms", methods=["GET"])
def get_forms():
    forms = list(forms_col.find())
    return jsonify({"forms": [serialize(f) for f in forms]})


@app.route("/api/forms/<form_id>", methods=["GET"])
def get_form(form_id):
    try:
        f = forms_col.find_one({"_id": ObjectId(form_id)})
        if not f:
            f = forms_col.find_one({"id": form_id})
    except Exception:
        f = forms_col.find_one({"id": form_id})
    if not f:
        return jsonify({"error": "Not found"}), 404
    return jsonify(serialize(f))


@app.route("/api/forms", methods=["POST"])
def create_form():
    data = request.json
    data["created_at"] = datetime.datetime.utcnow().isoformat()
    data["responses"] = 0
    result = forms_col.insert_one(data)
    return jsonify({"success": True, "id": str(result.inserted_id)})


@app.route("/api/forms/<form_id>", methods=["DELETE"])
def delete_form(form_id):
    try:
        forms_col.delete_one({"_id": ObjectId(form_id)})
    except Exception:
        forms_col.delete_one({"id": form_id})
    responses_col.delete_many({"form_id": form_id})
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════════════════════
# RESPONSES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/responses", methods=["POST"])
def submit_response():
    data = request.json
    data["submitted_at"] = datetime.datetime.utcnow().isoformat()
    responses_col.insert_one(data)
    # Update response count
    try:
        forms_col.update_one({"_id": ObjectId(data["form_id"])}, {"$inc": {"responses": 1}})
    except Exception:
        forms_col.update_one({"id": data["form_id"]}, {"$inc": {"responses": 1}})
    return jsonify({"success": True})


@app.route("/api/responses/<form_id>", methods=["GET"])
def get_responses(form_id):
    resps = list(responses_col.find({"form_id": form_id}))
    return jsonify({"responses": [serialize(r) for r in resps]})


# ══════════════════════════════════════════════════════════════════════════════
# ML PREDICTION
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    # Features: form_type, num_questions, num_responses, avg_answer_length, submission_hour
    features = [
        data.get("form_type_enc", 0),
        data.get("num_questions", 5),
        data.get("num_responses", 0),
        data.get("avg_answer_length", 20),
        data.get("submission_hour", 12),
    ]

    if ml_model:
        pred = ml_model.predict([features])[0]
        labels = {0: "Negative Feedback", 1: "Neutral Feedback", 2: "Positive Feedback"}
        result = labels.get(pred, "Neutral Feedback")
    else:
        # Rule-based fallback
        n = data.get("num_responses", 0)
        avg = data.get("avg_answer_length", 20)
        if n > 10 and avg > 30:
            result = "Positive Feedback"
        elif n < 3:
            result = "Neutral Feedback"
        else:
            result = "Neutral Feedback"

    return jsonify({"prediction": result})


# ══════════════════════════════════════════════════════════════════════════════
# GENERATIVE AI
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    data = request.json
    topic = data.get("topic", "general feedback")
    num = min(int(data.get("num_questions", 5)), 10)
    q_type = data.get("question_type", "mixed")

    prompt = (
        f"Generate {num} survey questions for the topic: '{topic}'.\n"
        f"Question type preference: {q_type}.\n"
        f"For MCQ questions, list options in brackets like (Option A / Option B / Option C).\n"
        f"Number each question. Keep language simple and conversational.\n"
        f"Only output the questions, no explanation."
    )

    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return jsonify({"questions": response.text.strip()})
        except Exception as e:
            print(f"[GenAI Error] {e}")

    # Fallback
    fallback = {
        "mixed": [
            f"How satisfied are you with {topic}? (Very satisfied / Satisfied / Neutral / Unsatisfied)",
            f"What did you enjoy the most about {topic}?",
            f"Would you recommend this to someone else? (Yes / Maybe / No)",
            f"What could we improve about {topic}?",
            f"On a scale of 1–5, how likely are you to return?"
        ],
        "text": [
            f"Describe your overall experience with {topic}.",
            f"What went well?",
            f"What could be done better?",
            f"Any suggestions or comments?",
            f"Is there anything else you would like to share?"
        ]
    }
    qs = fallback.get(q_type, fallback["mixed"])[:num]
    return jsonify({"questions": "\n\n".join(f"{i+1}. {q}" for i, q in enumerate(qs))})


@app.route("/api/generate-insight", methods=["POST"])
def generate_insight():
    data = request.json
    form_title = data.get("form_title", "survey")
    total = data.get("total", 0)
    responses = data.get("responses", [])

    # Prepare a summary for the prompt
    sample_answers = []
    for r in responses[:10]:
        for k, v in (r.get("answers") or {}).items():
            if v:
                sample_answers.append(str(v))

    prompt = (
        f"You are analyzing survey responses for: '{form_title}'.\n"
        f"Total responses: {total}.\n"
        f"Sample answers: {'; '.join(sample_answers[:20])}.\n\n"
        f"Write a 3–5 sentence plain-English summary of the key findings. "
        f"Mention what went well, what needs improvement, and one recommendation. "
        f"Keep it natural and readable. Do not use bullet points."
    )

    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return jsonify({"insight": response.text.strip()})
        except Exception as e:
            print(f"[GenAI Error] {e}")

    # Fallback rule-based insight
    if total == 0:
        insight = "No responses have been collected yet. Share the form link to start gathering feedback."
    elif total < 5:
        insight = (
            f"The form '{form_title}' has received {total} response(s) so far. "
            "The sample size is still small, so definitive conclusions are not possible yet. "
            "It is recommended to collect at least 10 responses before drawing conclusions. "
            "Continue sharing the form to gather more input."
        )
    else:
        pos_words = ["great", "good", "excellent", "love", "helpful", "satisfied", "happy", "amazing"]
        neg_words = ["bad", "poor", "slow", "confused", "difficult", "issue", "problem", "worst"]
        pos = sum(1 for a in sample_answers if any(w in a.lower() for w in pos_words))
        neg = sum(1 for a in sample_answers if any(w in a.lower() for w in neg_words))
        tone = "positive" if pos >= neg else ("mixed" if pos > 0 else "somewhat critical")
        insight = (
            f"The '{form_title}' form collected {total} response(s) and the overall feedback was {tone}. "
            f"Respondents highlighted a few recurring themes in their answers. "
            f"{'Many participants expressed satisfaction with the experience.' if pos >= neg else 'Some respondents pointed out areas that need attention.'} "
            f"It is recommended to follow up on any specific concerns raised and continue monitoring feedback over time."
        )

    return jsonify({"insight": insight})


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
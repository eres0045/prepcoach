"""HTTP API for PrepCoach. One endpoint family per mode, plus status."""

import uuid

from flask import Blueprint, jsonify, request, send_from_directory

from . import dsa, interview, resume
from .model_client import get_provider, provider_status

bp = Blueprint("api", __name__)
_sessions = {}


def _provider():
    return get_provider()


@bp.route("/api/mode", methods=["GET"])
def mode():
    return jsonify(provider_status())


@bp.route("/api/interview/roles", methods=["GET"])
def roles():
    return jsonify({"roles": interview.ROLES, "levels": interview.LEVELS})


@bp.route("/api/interview/start", methods=["POST"])
def interview_start():
    data = request.get_json(force=True, silent=True) or {}
    try:
        session = interview.InterviewSession(
            data.get("role", ""), data.get("level", ""), _provider())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    session_id = uuid.uuid4().hex
    _sessions[session_id] = session
    return jsonify({
        "session_id": session_id,
        "question": session.next_question(),
        "questions_total": interview.QUESTIONS_PER_SESSION,
    })


@bp.route("/api/interview/answer", methods=["POST"])
def interview_answer():
    data = request.get_json(force=True, silent=True) or {}
    session = _sessions.get(data.get("session_id", ""))
    if session is None:
        return jsonify({"error": "Unknown session"}), 404
    nxt = session.answer(data.get("answer", ""))
    if nxt is None:
        return jsonify({"finished": True, "debrief": session.debrief()})
    return jsonify({"finished": False, "question": nxt})


@bp.route("/api/resume", methods=["POST"])
def resume_review():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("resume_text", "")
    if not text.strip():
        return jsonify({"error": "Paste resume text first."}), 400
    return jsonify(resume.analyse(text))


@bp.route("/api/dsa/problems", methods=["GET"])
def dsa_problems():
    topic = request.args.get("topic")
    problems = dsa.PROBLEMS
    if topic:
        problems = [p for p in problems if p["topic"] == topic]
    return jsonify({
        "topics": dsa.TOPICS,
        "problems": [{k: p[k] for k in
                      ("id", "title", "topic", "difficulty", "statement",
                       "examples", "starter", "edge_cases")}
                     for p in problems],
    })


@bp.route("/api/dsa/hint", methods=["POST"])
def dsa_hint():
    data = request.get_json(force=True, silent=True) or {}
    try:
        return jsonify(dsa.hint(data.get("problem_id", ""),
                                int(data.get("level", 0))))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@bp.route("/api/dsa/review", methods=["POST"])
def dsa_review():
    data = request.get_json(force=True, silent=True) or {}
    try:
        return jsonify(dsa.review_solution(
            data.get("problem_id", ""), data.get("code", ""), _provider()))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def register(app):
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

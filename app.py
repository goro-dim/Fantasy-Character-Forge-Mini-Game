# app.py
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os, random
from character_generator import QUESTIONS, init_stats, synthesize, STAT_KEYS

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FORGE_SECRET_KEY", os.urandom(24))


# Helpers
def get_stats():
    if "stats" not in session:
        session["stats"] = init_stats()
    return session["stats"]

def save_stats(stats):
    session["stats"] = stats

@app.route("/")
def index():
    # Reset session for a new run
    session.clear()
    return render_template("index.html")

@app.route("/quiz/<int:qid>", methods=["GET", "POST"])
def quiz(qid):
    # qid is 0-based index for QUESTIONS
    if qid < 0 or qid >= len(QUESTIONS):
        return redirect(url_for("index"))
    stats = get_stats()
    q = QUESTIONS[qid]
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice in q["opts"]:
            _, delta = q["opts"][choice]
            # Apply deltas to stats
            for k, v in delta.items():
                stats[k] = stats.get(k, 0) + v
            # clamp small sanity bounds (same as in generator)
            for k in stats:
                if stats[k] < -10: stats[k] = -10
                if stats[k] > 100: stats[k] = 100
            save_stats(stats)
            next_q = qid + 1
            if next_q >= len(QUESTIONS):
                return redirect(url_for("result"))
            else:
                return redirect(url_for("quiz", qid=next_q))
    # Render question page
    # Provide fingerprint for progress bar (1-indexed)
    progress = {"current": qid+1, "total": len(QUESTIONS)}
    return render_template("quiz.html", question=q, qid=qid, progress=progress)

@app.route("/result")
def result():
    stats = get_stats()
    # Convert keys to ensure deterministic ordering for synthesize (it expects keys present)
    for k in STAT_KEYS:
        if k not in stats:
            stats[k] = 0
    # Use random seed for variety
    seed = random.randint(0, 2**30)
    char = synthesize(stats, seed=seed)
    # Save last character to session for potential export
    session["last_character"] = char
    return render_template("result.html", char=char)

@app.route("/static/<path:path>")
def static_proxy(path):
    # Serve static files (convenience for some deployments)
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

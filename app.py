"""
app.py - Main Flask application for AI Knowledge Helper.

FIX: PDF text is stored on disk (not in session cookie) to avoid the 4KB browser limit.
     Session only stores a small reference key pointing to the text file.
"""
import os
import uuid
import json
import tempfile
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv

from utils.pdf_extractor import extract_text_from_pdf
from utils.gemini_client import analyze_pdf_content, chat_with_context
from utils.audio_gen import generate_audio_summary
from utils.video_gen import generate_video

# ── Load environment variables ──
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ai-knowledge-helper-secret-2024")
# Increase max content length to 50MB for large PDFs
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_DIR = os.path.join(app.static_folder, "uploads")
CACHE_DIR  = os.path.join(app.static_folder, "cache")   # server-side text/content cache
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(app.static_folder, "audio"), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, "video"), exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", session.get("api_key", ""))


# ── Disk-based storage helpers (avoids 4KB session cookie limit) ──

def save_to_disk(data: str, prefix: str = "data") -> str:
    """Save a string to a temp file in CACHE_DIR. Returns the unique key."""
    key = f"{prefix}_{uuid.uuid4().hex}"
    path = os.path.join(CACHE_DIR, f"{key}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    return key


def load_from_disk(key: str) -> str:
    """Load a string from CACHE_DIR by key. Returns empty string if not found."""
    if not key:
        return ""
    path = os.path.join(CACHE_DIR, f"{key}.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_json_to_disk(data: dict, prefix: str = "json") -> str:
    """Save a dict as JSON to CACHE_DIR. Returns the unique key."""
    key = f"{prefix}_{uuid.uuid4().hex}"
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return key


def load_json_from_disk(key: str) -> dict:
    """Load a JSON dict from CACHE_DIR by key."""
    if not key:
        return {}
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────
# Routes
# ──────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/set-api-key", methods=["POST"])
def set_api_key():
    data = request.get_json()
    api_key = data.get("api_key", "").strip()
    if not api_key:
        return jsonify({"error": "API key cannot be empty"}), 400
    session["api_key"] = api_key
    session.modified = True
    return jsonify({"success": True})


@app.route("/upload", methods=["POST"])
def upload():
    """Upload a PDF, extract text, store text on disk, put key in session."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Save PDF file
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    file.save(file_path)

    # Extract text
    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            return jsonify({"error": "Could not extract text. The PDF may be scanned/image-based."}), 400
    except Exception as e:
        return jsonify({"error": f"PDF extraction failed: {str(e)}"}), 500

    # Store text on disk, keep only small key in session
    text_key = save_to_disk(text, prefix="pdf_text")
    session["pdf_text_key"] = text_key
    session["pdf_filename"] = file.filename[:100]   # keep short
    session["pdf_path"] = file_path
    session["content_key"] = ""  # reset any old processed content
    session.modified = True

    return jsonify({
        "success": True,
        "filename": file.filename,
        "char_count": len(text),
        "preview": text[:300] + "..." if len(text) > 300 else text
    })


@app.route("/process", methods=["POST"])
def process():
    """Load PDF text from disk, send to Gemini, cache structured content."""
    text_key = session.get("pdf_text_key", "")
    pdf_text = load_from_disk(text_key)
    if not pdf_text:
        return jsonify({"error": "No PDF content found. Please upload a PDF first."}), 400

    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "Gemini API key not set. Add it via the ⚙️ Settings button."}), 401

    try:
        content = analyze_pdf_content(pdf_text, api_key)
        # Save content to disk (may be large JSON)
        content_key = save_json_to_disk(content, prefix="content")
        session["content_key"] = content_key
        session.modified = True
        return jsonify({"success": True, "content": content})
    except Exception as e:
        return jsonify({"error": f"Gemini processing failed: {str(e)}"}), 500


@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    content_key = session.get("content_key", "")
    content = load_json_from_disk(content_key)
    summary = content.get("summary", "")
    if not summary:
        data = request.get_json() or {}
        summary = data.get("summary", "")
    if not summary:
        return jsonify({"error": "No summary available. Process a PDF first."}), 400

    try:
        audio_path = generate_audio_summary(summary)
        # Store absolute path for video gen use
        session["audio_path"] = os.path.join(app.static_folder, audio_path)
        session.modified = True
        return jsonify({"success": True, "audio_url": f"/static/{audio_path}"})
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500


@app.route("/generate-video", methods=["POST"])
def generate_video_route():
    content_key = session.get("content_key", "")
    content = load_json_from_disk(content_key)
    key_concepts = content.get("key_concepts", [])
    subject_tags = content.get("subject_tags", ["Knowledge"])
    summary = content.get("summary", "")
    is_stem = content.get("is_stem", False)

    if not key_concepts:
        return jsonify({"error": "No content available. Process a PDF first."}), 400

    try:
        # Check if audio exists, if not generate it on the fly for the video
        audio_abs_path = session.get("audio_path")
        if not audio_abs_path or not os.path.exists(audio_abs_path):
            if summary:
                rel_audio = generate_audio_summary(summary)
                audio_abs_path = os.path.join(app.static_folder, rel_audio)
                session["audio_path"] = audio_abs_path
                session.modified = True

        video_path = generate_video(
            key_concepts=key_concepts,
            subject_tags=subject_tags,
            summary=summary,
            is_stem=is_stem,
            audio_path=audio_abs_path
        )
        return jsonify({"success": True, "video_url": f"/static/{video_path}"})
    except Exception as e:
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400

    text_key = session.get("pdf_text_key", "")
    pdf_text = load_from_disk(text_key)
    if not pdf_text:
        return jsonify({"error": "No document loaded. Please upload a PDF first."}), 400

    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "Gemini API key not set."}), 401

    try:
        answer = chat_with_context(question, pdf_text, history, api_key)
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@app.route("/check-key", methods=["GET"])
def check_key():
    api_key = get_api_key()
    return jsonify({"has_key": bool(api_key)})


if __name__ == "__main__":
    print("=" * 50)
    print("  AI Knowledge Helper — Flask App")
    print("  Visit: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)

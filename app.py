
import os
import json
import uuid
import base64
from pathlib import Path
import io
from PIL import Image

import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3-vl:2b"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ollama_analyze(image_bytes):
# Resize large images to reduce local AI processing time
    with Image.open(io.BytesIO(image_bytes)) as img:
        img.thumbnail((768, 768))
        img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80, optimize=True)

        image_base64 = base64.b64encode(
        buffer.getvalue()
        ).decode("utf-8")
    prompt = """
    Analyse this image carefully.

    Return ONLY valid JSON in this exact structure:
    {
      "caption": "A detailed description of the image",
      "tags": ["tag1", "tag2", "tag3"],
      "objects": ["object1", "object2"],
      "extracted_text": "Text visible in the image, or empty string"
    }

    Do not include markdown or explanations outside the JSON.
    Only mention objects and text that are actually visible.
    """

    payload = {
    "model": OLLAMA_MODEL,
    "messages": [
        {
            "role": "user",
            "content": prompt,
            "images": [image_base64]
        }
    ],
    "format": "json",
    "stream": False,
    "options": {
        "num_ctx": 2048
    }
}

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600
    )

    if not response.ok:
        raise RuntimeError(
            f"Ollama returned {response.status_code}: {response.text[:500]}"
        )

    answer = response.json()["message"]["content"]

    try:
        result = json.loads(answer)
    except json.JSONDecodeError:
        result = {
            "caption": answer,
            "tags": [],
            "objects": [],
            "extracted_text": ""
        }

    tags = result.get("tags", [])
    objects = result.get("objects", [])
    extracted_text = result.get("extracted_text", "")

    return {
        "captionResult": {
            "text": result.get("caption", "No description generated."),
            "confidence": None
        },
        "tagsResult": {
            "values": [
                {"name": str(tag), "confidence": None}
                for tag in tags
            ]
        },
        "objectsResult": {
            "values": [
                {"object": str(obj), "confidence": None}
                for obj in objects
            ]
        },
        "readResult": {
            "blocks": [
                {"text": str(extracted_text)}
            ] if extracted_text else []
        },
        "_mode": "Ollama Local AI"
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "Please choose an image."}), 400

    image = request.files["image"]

    if not image.filename:
        return jsonify({"error": "No image selected."}), 400

    if not allowed_file(image.filename):
        return jsonify({
            "error": "Unsupported file type. Use PNG, JPG, JPEG, WEBP or BMP."
        }), 400

    safe_name = secure_filename(image.filename)
    data = image.read()

    if not data:
        return jsonify({"error": "The selected file is empty."}), 400

    extension = Path(safe_name).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{extension}"
    (UPLOAD_DIR / stored_name).write_bytes(data)

    try:
        result = ollama_analyze(data)
        return jsonify(result)

    except requests.ConnectionError:
        return jsonify({
            "error": "Could not connect to Ollama. Please make sure Ollama is running."
        }), 503

    except requests.Timeout:
        return jsonify({
            "error": "Image analysis took too long. Try again."
        }), 504

    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

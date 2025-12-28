import os
import uuid
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
AUDIO_QUALITY = "192k"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url or not url.startswith(("http://", "https://")):
        return jsonify({"error": "Invalid URL"}), 400

    job_id = str(uuid.uuid4())
    output_template = os.path.join(
        DOWNLOAD_FOLDER,
        f"{job_id}-%(title)s.%(ext)s"
    )

    try:
        subprocess.run(
            [
                "python", "-m", "yt_dlp",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", AUDIO_QUALITY,
                "-o", output_template,
                url
            ],
            check=True,
            timeout=300
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    files = []
    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.startswith(job_id) and file.endswith(".mp3"):
            files.append(file)

    return jsonify({
        "success": True,
        "files": files
    })

@app.route("/download-file/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

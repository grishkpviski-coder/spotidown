import os, glob, subprocess
from flask import Flask, request, send_file, jsonify, render_template

app = Flask(__name__)
DIR = "/tmp/dl"
os.makedirs(DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.get_json().get("url", "").strip()
    if "spotify.com/track" not in url:
        return jsonify({"error": "Нужна ссылка на трек Spotify"}), 400
    try:
        subprocess.run(["spotdl", url, "--output", DIR, "--format", "mp3"],
                       check=True, capture_output=True, timeout=120)
        files = glob.glob(os.path.join(DIR, "*.mp3"))
        if not files:
            return jsonify({"error": "Файл не найден"}), 500
        return send_file(max(files, key=os.path.getctime),
                         as_attachment=True, mimetype="audio/mpeg")
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Таймаут — попробуй ещё раз"}), 504
    except Exception:
        return jsonify({"error": "Не удалось скачать трек"}), 500

if __name__ == "__main__":
    app.run()

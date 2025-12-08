from flask import Flask, request, send_file, jsonify, render_template
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

progress_data = {"percentage": 0}

MIN_RESOLUTIONS = ["144p", "240p", "360p", "480p", "720p", "1080p"]

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            progress_data['percentage'] = float(percent)
        except:
            pass
    elif d['status'] == 'finished':
        progress_data['percentage'] = 100


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/video_info", methods=["POST"])
def video_info():
    url = request.form.get("url", "")
    if not url:
        return jsonify({"error": "URL missing"})

    ydl_opts = {"quiet": True, "skip_download": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        available = []
        for f in info.get("formats", []):
            if f.get("height"):
                available.append(str(f["height"]) + "p")

        final = sorted(set(available + MIN_RESOLUTIONS), key=lambda x: int(x.replace("p", "")))

        return jsonify({"resolutions": final})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    resolution = request.form.get("resolution")

    progress_data["percentage"] = 0

    output_file = f"video_{uuid.uuid4().hex}.mp4"

    ydl_opts = {
        "format": f"bestvideo[height={resolution.replace('p','')}] + bestaudio/best",
        "outtmpl": output_file,
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
        "quiet": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/progress")
def progress():
    return jsonify(progress_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

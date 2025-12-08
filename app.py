from flask import Flask, request, send_file, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

progress_data = {"percentage": 0}

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            percent = d['_percent_str'].replace('%', '').strip()
            progress_data['percentage'] = float(percent)
        except:
            pass
    elif d['status'] == 'finished':
        progress_data['percentage'] = 100


@app.route("/video_info", methods=["POST"])
def video_info():
    url = request.form.get("url", "")

    if not url:
        return jsonify({"error": "URL missing"})

    ydl_opts = {"quiet": True, "skip_download": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        resolutions = []
        for f in info["formats"]:
            if f.get("height"):
                resolutions.append(str(f["height"]) + "p")

        resolutions = sorted(list(set(resolutions)))

        return jsonify({"resolutions": resolutions})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    resolution = request.form.get("resolution")

    temp_file = "video.mp4"

    ydl_opts = {
        "format": f"bestvideo[height={resolution.replace('p','')}] + bestaudio/best",
        "outtmpl": temp_file,
        "progress_hooks": [progress_hook]
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(temp_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/progress")
def progress():
    return jsonify(progress_data)


@app.route("/")
def home():
    return "Backend Running Successfully!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

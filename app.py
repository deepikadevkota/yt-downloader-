from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import threading

app = Flask(__name__)

DOWNLOAD_PROGRESS = {"percent": 0}

# ---------- PROGRESS HOOK ----------
def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', "0%").replace("%", "")
            DOWNLOAD_PROGRESS["percent"] = float(percent)
        except:
            pass
    elif d['status'] == 'finished':
        DOWNLOAD_PROGRESS["percent"] = 100


# ---------- HOME PAGE ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- FETCH AVAILABLE RESOLUTIONS ----------
@app.route("/get_formats", methods=["POST"])
def get_formats():
    url = request.json.get("url")

    ydl_opts = {"quiet": True, "skip_download": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("height"):
                formats.append({
                    "format_id": f["format_id"],
                    "resolution": f"{f['height']}p",
                    "ext": f["ext"]
                })

        return jsonify({"formats": formats})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------- DOWNLOAD VIDEO ----------
@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data["url"]
    format_id = data["format_id"]
    folder = data["folder"]

    if not os.path.isdir(folder):
        return jsonify({"error": "Invalid folder path"}), 400

    DOWNLOAD_PROGRESS["percent"] = 0

    output_template = os.path.join(folder, "%(title)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "format": format_id,
        "progress_hooks": [progress_hook],
        "outtmpl": output_template
    }

    try:
        def run_download():
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        t = threading.Thread(target=run_download)
        t.start()

        return jsonify({"message": "Download started"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- PROGRESS API ----------
@app.route("/progress")
def progress():
    return jsonify(DOWNLOAD_PROGRESS)


if __name__ == "__main__":
    app.run(debug=True)

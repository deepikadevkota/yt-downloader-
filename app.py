from flask import Flask, render_template, request, send_file, jsonify
from pytubefix import YouTube
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress = {"percentage": 0}


def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    downloaded = total_size - bytes_remaining
    percent = int((downloaded / total_size) * 100)
    progress["percentage"] = percent


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_info", methods=["POST"])
def video_info():
    url = request.form.get("url")
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()

        resolutions = [stream.resolution for stream in streams if stream.resolution]

        return jsonify({"resolutions": resolutions})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url")
    resolution = request.form.get("resolution")

    try:
        progress["percentage"] = 0

        yt = YouTube(url, on_progress_callback=progress_function)
        stream = yt.streams.filter(res=resolution, progressive=True).first()

        if not stream:
            return "Resolution not available!"

        file_path = stream.download(output_path=DOWNLOAD_FOLDER)

        progress["percentage"] = 100
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/progress")
def get_progress():
    return jsonify(progress)


if __name__ == "__main__":
    app.run(debug=True, port=8000)

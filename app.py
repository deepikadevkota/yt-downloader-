from flask import Flask, render_template, request, send_file, jsonify
from pytubefix import YouTube
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress = {"percentage": 0}


def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percent = int((bytes_downloaded / total_size) * 100)
    progress["percentage"] = percent


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url")
    resolution = request.form.get("resolution")

    try:
        progress["percentage"] = 0

        yt = YouTube(url, on_progress_callback=progress_function)

        # Resolution Selector
        if resolution == "1080p":
            stream = yt.streams.filter(res="1080p", progressive=True).first()
        elif resolution == "720p":
            stream = yt.streams.filter(res="720p", progressive=True).first()
        elif resolution == "480p":
            stream = yt.streams.filter(res="480p", progressive=True).first()
        elif resolution == "360p":
            stream = yt.streams.filter(res="360p", progressive=True).first()
        else:
            stream = yt.streams.get_highest_resolution()

        if not stream:
            return f"Selected resolution {resolution} not available."

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

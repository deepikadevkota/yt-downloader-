from flask import Flask, render_template, request
from pytubefix import YouTube
import os
import re
import subprocess

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    url = request.form["url"]
    resolution = request.form["resolution"]

    try:
        yt = YouTube(url)

        safe_title = re.sub(r'[<>:"/\\|?*]', '', yt.title)[:150]

        stream = yt.streams.filter(resolution=resolution, progressive=True).first()

        if stream:
            filepath = stream.download(DOWNLOAD_FOLDER, filename=f"{safe_title}.mp4")
            return f"Download Complete! Saved as: {filepath}"

        video_stream = yt.streams.filter(resolution=resolution, adaptive=True).first()
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True).first()

        video_path = video_stream.download(DOWNLOAD_FOLDER, "temp_video.mp4")
        audio_path = audio_stream.download(DOWNLOAD_FOLDER, "temp_audio.mp3")

        final_output = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.mp4")

        cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{final_output}" -y'
        subprocess.call(cmd, shell=True)

        os.remove(video_path)
        os.remove(audio_path)

        return f"Download Complete! Saved as: {final_output}"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)

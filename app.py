from flask import Flask, render_template, request
from pytubefix import YouTube
import os
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        resolution = request.form["resolution"]

        try:
            yt = YouTube(url)

            # Safe filename
            safe_title = re.sub(r'[<>:"/\\|?*]', "", yt.title)[:150]

            # Try progressive (video+audio combined)
            stream = yt.streams.filter(resolution=resolution, progressive=True).first()

            if not stream:
                return render_template("index.html",
                                       error="Selected resolution not available!")

            file_path = stream.download(DOWNLOAD_FOLDER, filename=f"{safe_title}.mp4")

            return render_template("index.html",
                                   success=f"Download completed! Saved as: {file_path}",
                                   title=yt.title)

        except Exception as e:
            return render_template("index.html",
                                   error=f"Error: {str(e)}")

    return render_template("index.html")

if __name__ == "__main__":
    app.run()

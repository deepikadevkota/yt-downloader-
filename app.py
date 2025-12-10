from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form["url"]
        try:
            yt = YouTube(video_url)
            stream = yt.streams.get_highest_resolution()

            # File download path
            download_path = "downloads"
            if not os.path.exists(download_path):
                os.makedirs(download_path)

            file_path = stream.download(download_path)

            return send_file(file_path, as_attachment=True)

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

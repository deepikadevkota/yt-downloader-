
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

progress_data = {"percent": 0, "status": "idle"}

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            progress_data["percent"] = int(downloaded / total * 100)
            progress_data["status"] = "downloading"

    elif d['status'] == 'finished':
        progress_data["percent"] = 100
        progress_data["status"] = "finished"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    quality = request.json['quality']

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return jsonify({"status": "done"})

@app.route('/progress')
def progress():
    return jsonify(progress_data)

if __name__ == '__main__':
    app.run(debug=True)

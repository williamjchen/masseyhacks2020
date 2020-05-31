from flask import Flask, render_template, request, send_file
from video_summarize import VideoSummarize
app = Flask(__name__)

app.config['SECRET_KEY'] = '1fefead00aeba32d6ad65e9ab5ce6466'


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        user = request.form["fname"]
        summary = VideoSummarize(user)
        summary.summarize()
        return send_file("summarized.mp4", as_attachment=True)
    else:
        return render_template('form.html')

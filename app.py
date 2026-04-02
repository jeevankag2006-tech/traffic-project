from flask import Flask, render_template, request, redirect, Response, jsonify, send_from_directory
import os

from ai_traffic import process_video_live, generate_video

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USERNAME = "jeevan"
PASSWORD = "123456"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            return redirect('/dashboard')
        else:
            return "Wrong Login"
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist("videos")

        for i, file in enumerate(files):
            file.save(os.path.join(UPLOAD_FOLDER, f"lane{i+1}.mp4"))

        return redirect('/result')

    return render_template('upload.html')


# MAIN PAGE
@app.route('/result')
def result():

    counts = []
    ambulances = []
    speeds = []

    for i in range(1, 5):
        path = f"uploads/lane{i}.mp4"
        count, amb, speed = process_video_live(path)

        counts.append(count)
        ambulances.append(amb)
        speeds.append(speed)

    return render_template(
        "result.html",
        counts=counts,
        ambulances=ambulances,
        speeds=speeds
    )


# LIVE VIDEO STREAM
@app.route('/video/<int:lane>')
def video(lane):
    path = f"uploads/lane{lane}.mp4"

    return Response(
        generate_video(path),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# STATIC UPLOADED FILES
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# 🔥 LIVE DATA API
@app.route('/data')
def data():

    counts = []
    ambulances = []
    speeds = []

    for i in range(1, 5):
        path = f"uploads/lane{i}.mp4"
        count, amb, speed = process_video_live(path)

        counts.append(count)
        ambulances.append(amb)
        speeds.append(speed)

    return jsonify({
        "counts": counts,
        "ambulances": ambulances,
        "speeds": speeds
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)

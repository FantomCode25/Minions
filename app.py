from flask import Flask, render_template, Response, request, jsonify
import cv2
import time
from emotion_utils import detect_emotion_and_log

app = Flask(__name__)
camera = cv2.VideoCapture(0)
last_detection_time = 0
last_emotion = None
current_username = "Guest"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-username', methods=['POST'])
def set_username():
    global current_username
    current_username = request.form['username']
    return jsonify({"status": "success", "username": current_username})

def generate_frames():
    global last_detection_time, last_emotion

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Emotion detection every 1.5 seconds
            current_time = time.time()
            if current_time - last_detection_time > 1.5:
                last_detection_time = current_time
                emotion, message = detect_emotion_and_log(frame, current_username)
                if emotion != last_emotion:
                    print(f"User: {current_username} | Emotion: {emotion} | Message: {message}")
                    last_emotion = emotion

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/get-latest-emotion', methods=['GET'])
def get_latest_emotion():
    return jsonify({
        "emotion": last_emotion if last_emotion else "Detecting...",
        "username": current_username
    })


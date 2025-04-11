import cv2
import tkinter as tk
from PIL import Image, ImageTk
from emotion_utils import detect_emotion
import threading

cap = None
is_camera_running = False

def update_frame():
    global cap, is_camera_running
    if cap and is_camera_running:
        ret, frame = cap.read()
        if ret:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (400, 300))
            img = ImageTk.PhotoImage(Image.fromarray(img))
            camera_label.config(image=img)
            camera_label.image = img
        camera_label.after(10, update_frame)

def start_camera():
    global cap, is_camera_running
    if not is_camera_running:
        cap = cv2.VideoCapture(0)
        is_camera_running = True
        update_frame()

def stop_camera():
    global cap, is_camera_running
    if cap:
        is_camera_running = False
        cap.release()
        camera_label.config(image='')

def analyze_frame():
    global cap
    if cap and is_camera_running:
        ret, frame = cap.read()
        if ret:
            emotion, message = detect_emotion(frame)
            result_label.config(text=f"Emotion: {emotion}\n{message}")

# GUI setup
window = tk.Tk()
window.title("Facial Emotion Detector - DeepFace")
window.geometry("500x500")
window.configure(bg="white")

tk.Label(window, text="Facial Emotion Recognition", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

camera_label = tk.Label(window)
camera_label.pack()

btn_frame = tk.Frame(window, bg="white")
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="📸 Start Camera", command=start_camera, bg="#2196F3", fg="white", font=("Helvetica", 12))
start_btn.grid(row=0, column=0, padx=10)

capture_btn = tk.Button(btn_frame, text="🎯 Analyze Emotion", command=lambda: threading.Thread(target=analyze_frame).start(), bg="#4CAF50", fg="white", font=("Helvetica", 12))
capture_btn.grid(row=0, column=1, padx=10)

stop_btn = tk.Button(btn_frame, text="❌ Stop Camera", command=stop_camera, bg="#F44336", fg="white", font=("Helvetica", 12))
stop_btn.grid(row=0, column=2, padx=10)

result_label = tk.Label(window, text="", font=("Helvetica", 12), wraplength=450, bg="white")
result_label.pack(pady=20)

window.mainloop()

import cv2
import tkinter as tk
from PIL import Image, ImageTk
from emotion_utils import detect_emotion_and_log
import threading
import time

cap = None
is_camera_running = False
current_username = ""
last_emotion = None
last_detection_time = 0

def update_frame():
    global cap, is_camera_running, last_emotion, last_detection_time

    if cap and is_camera_running:
        ret, frame = cap.read()
        if ret:
            # Show frame in GUI
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (400, 300))
            img = ImageTk.PhotoImage(Image.fromarray(img))
            camera_label.config(image=img)
            camera_label.image = img

            # Detect emotion every 1.5 seconds
            current_time = time.time()
            if current_time - last_detection_time >= 1.5:
                last_detection_time = current_time

                def analyze_and_update():
                    global last_emotion
                    emotion, message = detect_emotion_and_log(frame, current_username)
                    if emotion != last_emotion:
                        last_emotion = emotion
                        result_label.config(text=f"Emotion: {emotion}\n{message}")

                threading.Thread(target=analyze_and_update).start()

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

def save_username():
    global current_username
    current_username = name_entry.get().strip()
    if current_username:
        username_frame.pack_forget()
        main_frame.pack()
    else:
        error_label.config(text="Please enter your name!")

# GUI setup
window = tk.Tk()
window.title("Real-Time Facial Emotion Detector")
window.geometry("500x550")
window.configure(bg="white")

# Username input screen
username_frame = tk.Frame(window, bg="white")
username_frame.pack(pady=50)

tk.Label(username_frame, text="Enter your name:", font=("Helvetica", 14), bg="white").pack()
name_entry = tk.Entry(username_frame, font=("Helvetica", 14))
name_entry.pack(pady=10)
tk.Button(username_frame, text="Start", command=save_username, font=("Helvetica", 12),
          bg="#2196F3", fg="white").pack(pady=5)
error_label = tk.Label(username_frame, text="", fg="red", bg="white")
error_label.pack()

# Main app screen
main_frame = tk.Frame(window, bg="white")

tk.Label(main_frame, text="Real-Time Facial Emotion Recognition", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)

camera_label = tk.Label(main_frame)
camera_label.pack()

btn_frame = tk.Frame(main_frame, bg="white")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="📸 Start Camera", command=start_camera, bg="#2196F3", fg="white", font=("Helvetica", 12)).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="❌ Stop Camera", command=stop_camera, bg="#F44336", fg="white", font=("Helvetica", 12)).grid(row=0, column=1, padx=10)

result_label = tk.Label(main_frame, text="", font=("Helvetica", 12), wraplength=450, bg="white")
result_label.pack(pady=20)

window.mainloop()

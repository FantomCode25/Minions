// Declare the Socket.IO connection once
const socket = io("http://localhost:8080");

document.addEventListener("DOMContentLoaded", () => {
  let stream;
  let audioBlob;
  let isRecording = false; // Flag to track the recording state
  let isWebcamActive = false; // Flag to track webcam state
  let mediaRecorder;
  let webcamStream;
  let frameInterval;

  // Get DOM elements
  const sendButton = document.getElementById("send-btn");
  const micButton = document.getElementById("mic-btn");
  const videoButton = document.getElementById("video-btn");
  const textInput = document.getElementById("text-input");
  const micStatus = document.getElementById("mic-status");
  const videoElement = document.getElementById("video");
  const videoContainer = document.getElementById("video-container");

  // Send text input to the server
  if (sendButton) {
    sendButton.addEventListener("click", () => {
      if (textInput) {
        const text = textInput.value;
        socket.emit("text", { message: text });
        alert(`You sent: ${text}`);
        console.log(`Text sent: ${text}`);
      } else {
        console.error("Text input element not found.");
      }
    });
  }

  // Handle server response for text
  socket.on("text_response", (data) => {
    console.log(`Server response: ${data.message}`);
  });

  // Audio handling
  if (micButton && micStatus) {
    micButton.addEventListener("click", async () => {
      if (!isRecording) {
        try {
          // Start recording
          stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          const audioChunks = [];

          mediaRecorder.ondataavailable = (event) =>
            audioChunks.push(event.data);

          mediaRecorder.onstop = async () => {
            audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            console.log("Audio blob created:", audioBlob);

            try {
              const buffer = await audioBlob.arrayBuffer();
              socket.emit("audio", buffer); // Emit audio data to the server
            } catch (error) {
              console.error("Error sending audio data:", error);
            }
          };

          mediaRecorder.start();
          micStatus.textContent = "🎙️ Recording...";
          micButton.style.backgroundColor = "red";
          console.log("Recording started.");
          isRecording = true;
        } catch (error) {
          micStatus.textContent = "Ready";
          console.error("Microphone error:", error);
          alert(`Unable to access microphone: ${error.name}`);
        }
      } else {
        // Stop recording
        mediaRecorder.stop();
        stream.getTracks().forEach((track) => track.stop());
        micStatus.textContent = "Recording stopped.";
        micButton.style.backgroundColor = "";
        console.log("Recording stopped.");
        isRecording = false;
      }
    });

    // Handle server response for audio
    socket.on("audio_response", (data) => {
      console.log(`Server response: ${data.message}`);
    });
  }

  // Video handling
  if (videoButton && videoElement && videoContainer) {
    videoButton.addEventListener("click", async () => {
      if (frameInterval) {
        // Stop webcam and clear resources
        clearInterval(frameInterval);
        webcamStream.getTracks().forEach((track) => track.stop());
        videoElement.srcObject = null;
        videoContainer.style.display = "none";
        console.log("Webcam turned off.");
        isWebcamActive = false;
      } else {
        try {
          webcamStream = await navigator.mediaDevices.getUserMedia({
            video: true,
          });
          videoElement.srcObject = webcamStream;
          videoContainer.style.display = "block";
          console.log("Webcam enabled successfully!");

          const canvas = document.createElement("canvas");
          const ctx = canvas.getContext("2d");

          frameInterval = setInterval(() => {
            canvas.width = videoElement.videoWidth || 640;
            canvas.height = videoElement.videoHeight || 480;
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            canvas.toBlob((blob) => {
              if (blob) {
                blob.arrayBuffer().then((buffer) => {
                  socket.emit("video", buffer); // Emit video frame to the server
                  console.log("Video frame sent to server.");
                });
              }
            }, "image/jpeg");
          }, 200); // Send frames every 200ms

          isWebcamActive = true;
        } catch (error) {
          console.error("Error accessing webcam:", error);
          alert(`Unable to access webcam: ${error.message}`);
        }
      }
    });

    // Handle server response for video
    socket.on("video_response", (data) => {
      console.log(`Server response: ${data.message}`);
    });
  }
});

// Mood message display
function displayMoodMessage(mood) {
  alert(`You selected ${mood}. We're here to help! 💛`);
}

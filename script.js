let stream;
let audioBlob;
let isRecording = false; // Flag to track the recording state
let isWebcamActive = false; // Flag to track webcam state
let mediaRecorder;
let webcamStream;
let frameInterval;

let audioSocket; // WebSocket for audio handling
let videoSocket; // WebSocket for video handling

const WEBSOCKET_AUDIO_URL = "ws://localhost:8080/audio"; // WebSocket URL for audio
const WEBSOCKET_VIDEO_URL = "ws://localhost:8080/video"; // WebSocket URL for video

// Send button click handler
document.getElementById("send-btn").addEventListener("click", () => {
  const text = document.getElementById("text-input").value;
  alert(`You sent: ${text}`);
});

// Audio handling
document.addEventListener("DOMContentLoaded", () => {
  const micButton = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status");

  // Initialize and manage the audio WebSocket
  const initializeAudioSocket = () => {
    audioSocket = new WebSocket(WEBSOCKET_AUDIO_URL);

    audioSocket.onopen = () =>
      console.log("Audio WebSocket connection established.");
    audioSocket.onclose = () =>
      console.log("Audio WebSocket connection closed.");
    audioSocket.onerror = (error) =>
      console.error("Audio WebSocket error:", error);
  };

  // Ensure the audio WebSocket is open
  const ensureAudioSocketOpen = () =>
    new Promise((resolve, reject) => {
      if (audioSocket.readyState === WebSocket.OPEN) {
        resolve();
      } else if (audioSocket.readyState === WebSocket.CONNECTING) {
        audioSocket.addEventListener("open", resolve, { once: true });
      } else {
        console.log("Reinitializing audio WebSocket...");
        initializeAudioSocket();
        audioSocket.addEventListener("open", resolve, { once: true });
      }
    });

  initializeAudioSocket();

  // Audio recording start/stop logic
  micButton.addEventListener("click", async () => {
    if (!isRecording) {
      try {
        // Start recording
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);

        mediaRecorder.onstop = async () => {
          audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          console.log("Audio blob created:", audioBlob);

          try {
            await ensureAudioSocketOpen();
            sendAudioData(audioBlob);
          } catch (error) {
            console.error("WebSocket issue during stop event:", error);
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

  // Function to send audio data
  const sendAudioData = (audioBlob) => {
    if (audioSocket.readyState === WebSocket.OPEN) {
      audioBlob
        .arrayBuffer()
        .then((buffer) => {
          const header = new TextEncoder().encode("audio:");
          const audioData = new Uint8Array(header.length + buffer.byteLength);

          audioData.set(header, 0);
          audioData.set(new Uint8Array(buffer), header.length);

          audioSocket.send(audioData);
          console.log("Audio data sent successfully.");
        })
        .catch((error) => console.error("Failed to send audio data:", error));
    } else {
      console.warn("Audio WebSocket is not open. Cannot send audio data.");
    }
  };
});

// Video handling
document.getElementById("video-btn").addEventListener("click", async () => {
  const videoElement = document.getElementById("video");
  const videoContainer = document.getElementById("video-container");

  // Initialize and manage the video WebSocket
  const initializeVideoSocket = () => {
    videoSocket = new WebSocket(WEBSOCKET_VIDEO_URL);

    videoSocket.onopen = () =>
      console.log("Video WebSocket connection established.");
    videoSocket.onclose = () =>
      console.log("Video WebSocket connection closed.");
    videoSocket.onerror = (error) =>
      console.error("Video WebSocket error:", error);
  };

  if (!videoSocket || videoSocket.readyState === WebSocket.CLOSED) {
    initializeVideoSocket();
  }

  if (isWebcamActive) {
    // Stop webcam and clear resources
    clearInterval(frameInterval);
    webcamStream.getTracks().forEach((track) => track.stop());
    videoElement.srcObject = null;
    videoContainer.style.display = "none";
    console.log("Webcam turned off.");
    isWebcamActive = false;
  } else {
    try {
      // Start webcam
      webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoElement.srcObject = webcamStream;
      videoContainer.style.display = "block";
      videoContainer.scrollIntoView({ behavior: "smooth" });
      console.log("Webcam enabled successfully!");

      isWebcamActive = true;

      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      // Send video frames every 200ms
      frameInterval = setInterval(() => {
        if (videoSocket.readyState === WebSocket.OPEN) {
          canvas.width = videoElement.videoWidth || 640; // Default size if unavailable
          canvas.height = videoElement.videoHeight || 480;
          ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

          canvas.toBlob((blob) => {
            if (blob) {
              blob.arrayBuffer().then((buffer) => {
                const header = new TextEncoder().encode("video:");
                const videoData = new Uint8Array(
                  header.length + buffer.byteLength
                );

                videoData.set(header, 0);
                videoData.set(new Uint8Array(buffer), header.length);

                videoSocket.send(videoData);
                console.log("Video frame sent to server.");
              });
            }
          }, "image/jpeg");
        } else {
          console.warn(
            "Video WebSocket is not open. Skipping frame transmission."
          );
        }
      }, 200); // Send frames every 200ms
    } catch (error) {
      console.error("Error accessing webcam:", error);
      alert(`Unable to access webcam: ${error.message}`);
    }
  }
});

// Mood message display
function displayMoodMessage(mood) {
  alert(`You selected ${mood}. We're here to help! 💛`);
}

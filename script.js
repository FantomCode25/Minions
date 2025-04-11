let stream;
let audioBlob;
let isReinitializing = false; // Flag to track WebSocket reinitialization
const WEBSOCKET_URL = "ws://localhost:8080"; // WebSocket URL

document.getElementById("send-btn").addEventListener("click", () => {
  const text = document.getElementById("text-input").value;
  alert(`You sent: ${text}`);
});

document.addEventListener("DOMContentLoaded", () => {
  const micButton = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status");

  let isRecording = false; // Flag to track the recording state
  let mediaRecorder;
  const audioChunks = [];

  // Initialize WebSocket connection
  let socket = initializeWebSocket();

  // Function to initialize or reinitialize WebSocket
  function initializeWebSocket() {
    console.log("Initializing WebSocket...");
    const ws = new WebSocket(WEBSOCKET_URL);

    ws.onopen = () => {
      console.log("WebSocket is open and ready.");
      isReinitializing = false;
    };

    ws.onerror = (error) => {
      console.error("WebSocket encountered an error:", error);
      isReinitializing = false;
    };

    ws.onclose = () => {
      console.warn("WebSocket closed. Consider reinitializing if needed.");
    };

    return ws;
  }

  // Function to ensure the WebSocket is open
  function ensureWebSocketOpen(audioBlob) {
    return new Promise((resolve, reject) => {
      if (socket.readyState === WebSocket.OPEN) {
        resolve(); // WebSocket is already open
      } else if (socket.readyState === WebSocket.CONNECTING) {
        socket.addEventListener(
          "open",
          () => {
            console.log("WebSocket connected during ensureOpen.");
            resolve();
          },
          { once: true }
        );
      } else if (
        socket.readyState === WebSocket.CLOSING ||
        socket.readyState === WebSocket.CLOSED
      ) {
        console.log("Reinitializing WebSocket...");
        if (!isReinitializing) {
          isReinitializing = true;
          socket = initializeWebSocket();
          socket.addEventListener(
            "open",
            () => {
              console.log("WebSocket reinitialized and ready.");
              resolve();
            },
            { once: true }
          );
        } else {
          console.warn("WebSocket reinitialization already in progress.");
          reject("WebSocket is still reinitializing.");
        }
      } else {
        reject("Unexpected WebSocket state: " + socket.readyState);
      }
    });
  }

  // Function to send audio data
  function sendAudioData(audioBlob) {
    if (!audioBlob) {
      console.error("audioBlob is undefined. Cannot send audio data.");
      return;
    }
    if (socket.readyState === WebSocket.OPEN) {
      audioBlob
        .arrayBuffer()
        .then((buffer) => {
          socket.send(buffer);
          console.log("Audio data sent successfully.");
        })
        .catch((error) => {
          console.error("Failed to send audio data:", error);
        });
    } else {
      console.warn("WebSocket is not open. Cannot send audio data.");
    }
  }

  // Recording start/stop logic
  micButton.addEventListener("click", async () => {
    if (!isRecording) {
      // Start recording
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          console.log("audioBlob created:", audioBlob);
          audioChunks.length = 0; // Clear the audioChunks array

          ensureWebSocketOpen(audioBlob)
            .then(() => {
              sendAudioData(audioBlob);
            })
            .catch((error) => {
              console.error("WebSocket issue during stop event:", error);
            });
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
});

document.getElementById("camera-btn").addEventListener("click", () => {
  alert("Camera activated! Analyzing facial expressions...");
});

function displayMoodMessage(mood) {
  alert(`You selected ${mood}. We're here to help! 💛`);
}

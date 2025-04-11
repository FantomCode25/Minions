let stream;
let audioBlob;
document.getElementById("send-btn").addEventListener("click", () => {
  const text = document.getElementById("text-input").value;
  alert(`You sent: ${text}`);
});

document.addEventListener("DOMContentLoaded", () => {
  const micButton = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status");

  let isRecording = false; // Flag to track the recording state
  let mediaRecorder;
  let stream;
  const audioChunks = []; // Declare audioChunks globally for reuse

  // Initialize WebSocket connection
  let socket = new WebSocket("ws://localhost:8080");

  if (socket.readyState !== WebSocket.OPEN) {
    console.log("Reinitializing WebSocket...");
    const newSocket = new WebSocket("ws://localhost:8080");

    newSocket.onopen = () => {
      console.log("WebSocket reinitialized and open.");
      sendAudioData(audioBlob); // Send data via new WebSocket
    };

    newSocket.onerror = (error) => {
      console.error("Error with reinitialized WebSocket:", error);
    };

    socket = newSocket; // Replace the old socket after successful reinitialization
  }

  // Function to ensure the WebSocket is open before sending data
  function ensureWebSocketOpen(socket, audioBlob) {
    return new Promise((resolve, reject) => {
      if (socket.readyState === WebSocket.OPEN) {
        resolve(); // WebSocket is already open
      } else if (socket.readyState === WebSocket.CONNECTING) {
        socket.addEventListener(
          "open",
          () => {
            console.log("WebSocket reconnected during sending.");
            sendAudioData(audioBlob); // Send data after reconnection
          },
          { once: true }
        );
      } else {
        console.log("Reinitializing WebSocket...");
        socket = new WebSocket("ws://localhost:8080/ws"); // Reinitialize WebSocket

        socket.onopen = () => {
          console.log("WebSocket reinitialized and open.");
          sendAudioData(audioBlob); // Send data via new WebSocket
        };

        socket.onerror = (error) => {
          console.error("Error with reinitialized WebSocket:", error);
          reject("Unable to send data due to WebSocket error.");
        };
      }
    });
  }

  // Function to send audio data
  function sendAudioData(audioBlob) {
    if (!audioBlob) {
      console.error("audioBlob is undefined. Cannot send audio data.");
      return; // Exit the function
    }
    audioBlob
      .arrayBuffer()
      .then((buffer) => {
        socket.send(buffer);
        console.log("Audio data sent successfully.");
      })
      .catch((error) => {
        console.error("Failed to send audio data:", error);
      });
  }

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
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          ensureWebSocketOpen(socket, audioBlob).catch((error) => {
            console.error("WebSocket issue during stop event:", error);
          });
        };

        mediaRecorder.start();
        micStatus.textContent = "🎙️ Recording...";
        micButton.style.backgroundColor = "red";
        console.log("Recording started.");
        isRecording = true; // Set the flag to true
      } catch (error) {
        micStatus.textContent = "Ready"; // Reset the status
        console.error("Microphone error:", error);
        alert(`Unable to access microphone: ${error.name}`);
      }
    } else {
      // Stop recording
      mediaRecorder.stop(); // Stop the MediaRecorder
      stream.getTracks().forEach((track) => track.stop()); // Stop the stream
      micStatus.textContent = "Recording stopped.";
      micButton.style.backgroundColor = "";
      console.log("Recording stopped.");
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      ensureWebSocketOpen(socket, audioBlob).catch((error) => {
        console.error("WebSocket issue during data sending:", error);
      });
      isRecording = false; // Reset the flag to false
    }
  });
});

document.getElementById("camera-btn").addEventListener("click", () => {
  alert("Camera activated! Analyzing facial expressions...");
  // Add camera input detection logic here
});

function showMood(mood) {
  alert(`You selected ${mood}. We're here to help! 💛`);
}

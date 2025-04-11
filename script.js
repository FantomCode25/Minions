document.getElementById("send-btn").addEventListener("click", () => {
  const text = document.getElementById("text-input").value;
  alert(`You sent: ${text}`);
});

document.getElementById("mic-btn").addEventListener("click", () => {
  alert("Mic activated! Monitoring tone variations...");
  // Add mic input detection logic here
});

document.getElementById("camera-btn").addEventListener("click", () => {
  alert("Camera activated! Analyzing facial expressions...");
  // Add camera input detection logic here
});

function showMood(mood) {
  alert(`You selected ${mood}. We're here to help! 💛`);
}
